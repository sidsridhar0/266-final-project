import json
import os
import random

os.environ.setdefault("SSL_CERT_FILE", "/opt/homebrew/etc/openssl@3/cert.pem")
os.environ.setdefault("REQUESTS_CA_BUNDLE", "/opt/homebrew/etc/openssl@3/cert.pem")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import numpy as np
import sacrebleu
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer, util
from sklearn.model_selection import KFold
from tqdm import tqdm

load_dotenv()

BASELINE_TEST_PATH = "results/baseline/test_baseline.json"
OUTPUT_PATH = "evaluation_results.txt"

K_FOLDS = 5
RANDOM_SEED = 42
DECODER_STS_SAMPLE_PER_FOLD = 20
LLM_JUDGE_SAMPLE_SIZE = 50
LLM_MODEL = "gpt-4o-mini"
ENCODER_MODEL_NAME = "all-mpnet-base-v2"

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

client = OpenAI(api_key=os.environ.get("OPENAI_API") or os.environ.get("OPENAI_API_KEY"))
sts_encoder = SentenceTransformer(ENCODER_MODEL_NAME)


def load_baseline_data(path):
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)
    references = [r["ground_truth_report"] for r in records]
    predictions = [r["baseline_report"] for r in records]
    return records, references, predictions


def compute_bleu(predictions, references):
    refs = [[ref] for ref in references]
    return sacrebleu.corpus_bleu(predictions, refs).score


def compute_encoder_sts(predictions, references):
    pred_emb = sts_encoder.encode(predictions, convert_to_tensor=True, show_progress_bar=False)
    ref_emb = sts_encoder.encode(references, convert_to_tensor=True, show_progress_bar=False)
    cosine_scores = util.cos_sim(pred_emb, ref_emb)
    return [cosine_scores[i][i].item() for i in range(len(predictions))]


def compute_decoder_sts(prediction, reference):
    prompt = f"""Evaluate the Semantic Textual Similarity (STS) between the following two sentences.
Score them on a scale from 1 (completely dissimilar) to 5 (exact same meaning).
Output ONLY the float number.

Sentence 1: {reference}
Sentence 2: {prediction}
"""
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        score_str = response.choices[0].message.content.strip()
        return (float(score_str) - 1) / 4.0
    except Exception:
        return None


def llm_judge_quality(reference, prediction):
    prompt = f"""You are an expert financial-news evaluator.
Given the reference (ground-truth) market report and a model-generated market report,
rate the holistic quality of the model-generated report on a scale of 1 to 10.
Consider fluency, structural coherence, and factual alignment with the reference.
Output ONLY the integer score.

Reference Report: {reference}
Model Report: {prediction}
"""
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return float(response.choices[0].message.content.strip())
    except Exception:
        return None


def mean_std(values):
    values = [v for v in values if v is not None]
    if not values:
        return 0.0, 0.0
    return float(np.mean(values)), float(np.std(values))


def run_kfold_sts_evaluation(references, predictions, lines):
    lines.append("=" * 70)
    lines.append("BASELINE MODEL - K-FOLD CROSS-VALIDATION + STS EVALUATION")
    lines.append("=" * 70)
    lines.append(f"Data source: {BASELINE_TEST_PATH}")
    lines.append(f"Total examples: {len(references)}")
    lines.append(f"K = {K_FOLDS} folds, random_seed = {RANDOM_SEED}")
    lines.append(f"Encoder STS model: {ENCODER_MODEL_NAME}")
    lines.append(f"Decoder STS judge model: {LLM_MODEL} ({DECODER_STS_SAMPLE_PER_FOLD} sampled examples/fold)")
    lines.append("")

    kf = KFold(n_splits=K_FOLDS, shuffle=True, random_state=RANDOM_SEED)
    indices = np.arange(len(references))

    fold_bleu = []
    fold_encoder_sts = []
    fold_decoder_sts = []

    for fold_idx, (_, test_idx) in enumerate(tqdm(list(kf.split(indices)), desc="K-Fold evaluation"), start=1):
        fold_refs = [references[i] for i in test_idx]
        fold_preds = [predictions[i] for i in test_idx]

        bleu = compute_bleu(fold_preds, fold_refs)
        encoder_scores = compute_encoder_sts(fold_preds, fold_refs)
        encoder_mean = float(np.mean(encoder_scores))

        sample_size = min(DECODER_STS_SAMPLE_PER_FOLD, len(fold_refs))
        sample_idx = random.sample(range(len(fold_refs)), sample_size)
        decoder_scores = [compute_decoder_sts(fold_preds[i], fold_refs[i]) for i in sample_idx]
        decoder_mean, decoder_std = mean_std(decoder_scores)

        fold_bleu.append(bleu)
        fold_encoder_sts.append(encoder_mean)
        fold_decoder_sts.append(decoder_mean)

        lines.append(f"Fold {fold_idx}/{K_FOLDS} (n={len(test_idx)}):")
        lines.append(f"  BLEU-4:                          {bleu:.2f}")
        lines.append(f"  Encoder STS (cosine similarity): {encoder_mean:.4f}")
        lines.append(f"  Decoder STS (LLM, n={sample_size}):          {decoder_mean:.4f} (std {decoder_std:.4f})")
        lines.append("")

    bleu_mean, bleu_std = mean_std(fold_bleu)
    enc_mean, enc_std = mean_std(fold_encoder_sts)
    dec_mean, dec_std = mean_std(fold_decoder_sts)

    lines.append("-" * 70)
    lines.append("Aggregate across folds (mean +/- std):")
    lines.append(f"  BLEU-4:                          {bleu_mean:.2f} +/- {bleu_std:.2f}")
    lines.append(f"  Encoder STS (cosine similarity): {enc_mean:.4f} +/- {enc_std:.4f}")
    lines.append(f"  Decoder STS (LLM-based):         {dec_mean:.4f} +/- {dec_std:.4f}")
    lines.append("")

    return {
        "bleu_per_fold": fold_bleu,
        "encoder_sts_per_fold": fold_encoder_sts,
        "decoder_sts_per_fold": fold_decoder_sts,
        "bleu_mean": bleu_mean,
        "bleu_std": bleu_std,
        "encoder_sts_mean": enc_mean,
        "encoder_sts_std": enc_std,
        "decoder_sts_mean": dec_mean,
        "decoder_sts_std": dec_std,
    }


def run_llm_judge_evaluation(records, references, predictions, lines):
    lines.append("=" * 70)
    lines.append("LLM-AS-A-JUDGE EVALUATION")
    lines.append("=" * 70)
    lines.append(f"Judge model: {LLM_MODEL}")
    lines.append("Models evaluated: baseline")
    lines.append("pb-t5 and nm-bart were skipped: no trained checkpoints or generated")
    lines.append("outputs for these models exist anywhere in this repository.")
    lines.append("")

    sample_size = min(LLM_JUDGE_SAMPLE_SIZE, len(references))
    sample_idx = random.sample(range(len(references)), sample_size)

    scores = []
    per_example = []
    for i in tqdm(sample_idx, desc="LLM-as-a-judge evaluation"):
        score = llm_judge_quality(references[i], predictions[i])
        scores.append(score)
        per_example.append((records[i]["market"], records[i]["date"], score))

    judge_mean, judge_std = mean_std(scores)

    lines.append(f"baseline (n={sample_size}, scale 1-10): {judge_mean:.2f} +/- {judge_std:.2f}")
    lines.append("")
    lines.append("Per-example scores (market, date, score):")
    for market, date, score in per_example:
        score_str = f"{score:.1f}" if score is not None else "N/A"
        lines.append(f"  {market:25s} {date:12s} {score_str}")
    lines.append("")

    return {
        "llm_judge_mean": judge_mean,
        "llm_judge_std": judge_std,
        "n_samples": sample_size,
    }


def main():
    records, references, predictions = load_baseline_data(BASELINE_TEST_PATH)

    lines = []
    lines.append("DataTales Evaluation Report")
    lines.append("")

    run_kfold_sts_evaluation(references, predictions, lines)
    run_llm_judge_evaluation(records, references, predictions, lines)

    report = "\n".join(lines)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\nWrote evaluation results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
