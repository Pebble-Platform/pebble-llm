# Block 4 — save the adapted encoder (the reusable artifact), then free MLM memory.
adapted_state = {k: v.detach().half().cpu() for k, v in enc_ref.state_dict().items()}
torch.save(adapted_state, f"{ART}/mlm_encoder.pt")
print(f"[MLM] saved adapted encoder -> {ART}/mlm_encoder.pt ({len(adapted_state)} tensors, fp16)")
del mlm, enc_ref, opt; torch.cuda.empty_cache()
print("memory freed")
