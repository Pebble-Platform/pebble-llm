# Block 7 — ABLATION arm B: MLM-ON (30%-mask domain-adapted encoder)
on = finetune("MLM-on (adapted)", adapted_state)
print("RESULT:", on)
