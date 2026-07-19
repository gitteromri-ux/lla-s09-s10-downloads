# RUNBOOK FIX V2 — final re-render (client presenting; execute immediately)

Supersedes RUNBOOK_OPTION_B.md. Any session with the HIGGSFIELD connector can run this.
Client-approved GO already given. No further approvals needed EXCEPT the 60-second
master veto (step 2) — post masters, wait max 5 minutes, then proceed unless STOP.

## End result (client's exact spec)
Every shot: real Courtney (pristine driver), seated with her back AGAINST the chair
backrest, chair snug (no dead space beside it), camera pulled back (split zoom:
camera B -20% to medium, camera A -10%), natural proportions, both angles alternating,
her exact monologue audio, no other changes.

## State (already done — do not redo)
- 28 PRISTINE driver chunks are uploaded into these confirmed Higgsfield media slots
  (chunk index -> media_id) in .pipeline/ and below; drivers were re-cut from the
  original WeTransfer footage at 1080p. Slots hold PRISTINE content as of this runbook.
  media ids (0..27 in order):
  b66c6ebc-4836-4935-bbb8-23d30a23856b, b2697efa-0930-47a3-aa60-6d0ba59b9a97,
  cab4ad73-cfa6-4035-85f3-e71250479e20, a45c537a-fb5f-4c25-99fb-9c1367e8ff7f,
  fadb5c5b-fd9d-4c86-bc0f-737a25362e2f, 8ce83b99-7a6c-4010-8a98-fc6485bca770,
  b79d350f-dec7-4d57-934d-8654caa7e7c8, fcae9c88-0142-41b8-aabe-af7330af0957,
  de10049f-478b-4091-9d64-b2879af5a5fe, 74491abf-e329-45c4-95c5-64d1c7791da3,
  39cc082f-b42b-4619-8e7d-6500673ad301, 956c4b5d-37df-4060-8eb1-3d91385335c2,
  f2878eef-7656-408b-b154-0e8e3c5d2974, 56f8ff3d-46d9-43b7-908c-4bfb352863a2,
  11e87dd6-582f-4557-ac1e-c6dc618c44b2, c674a115-43c2-47b6-8112-de791370b5f3,
  bbf3cd49-f67f-4cbc-88c6-b492f505c535, 0ab4979a-db2a-4709-8ba1-d9b76f5a59a9,
  0571bbe7-91e7-48b4-a0e9-2a42948129c2, 708b44ce-3d1e-4dbe-a39f-f910ee358dec,
  337af7bf-8b69-42cf-8c09-1f2d45719808, 6dc25670-48b5-4d2c-9e8c-47f718d3bdf6,
  2b495908-3544-4c12-a1b7-665ceeedfde6, e3d915e6-464e-457d-81af-6f1a9b43d6b3,
  18b971e9-207f-43c5-92f6-c45e76b0c3a9, a18cab16-4e8f-4627-9c1e-c6f92a034ffa,
  fa565bba-dc9a-4c22-9243-5acecc2353e4, e42fde1a-c8e0-4949-bcf7-a5fb724d7755
- Pristine full audio: deliverables/audio_full_0717.m4a (on main).
- Current masters (flawed, base for edits): wide A = image job 2c5c0e4c-b9ae-4942-a32e-9d7e21ff8108,
  close B = image job fef6b34b-1f5f-4697-b1e2-a1289a459e9f.
- Balance should be ~4900+ (client topped up). Full fleet = 26x135 + 72 + 81 = 3663 cr.
  Canary = 270. Masters = ~8. Verify with balance tool first.

## Steps
1. MASTERS (nano_banana_pro, 2k, 16:9, count 2 each, iterate until spec met):
   A-prompt: edit job 2c5c0e4c...: "Pull the camera back about 10 percent (wider view,
   whole chair visible with margin). The woman sits fully back, her back RESTING AGAINST
   the chair backrest, no gap. The chair is snug around her: narrower seat and armrests
   close to her body, no empty seat space visible beside her. Keep same woman, same room,
   same lighting, colors, grain. Photorealistic; change nothing else."
   B-prompt: edit job fef6b34b...: same chair/backrest language + "Pull the camera back
   about 20 percent to a MEDIUM shot (head to mid-thigh visible), she is farther from
   the camera. Change nothing else."
   AUDIT masters vs checklist (back touching backrest / snug chair / no side gap /
   wider frame). Pixel-compare with prior masters. Send both to client: "60-sec veto,
   auto-proceed".
2. CANARY: generate_video seedance_2_0 1080p std 15s, chunk 4 driver
   (fadb5c5b..., camera A master) AND chunk 5 driver (8ce83b99..., camera B master),
   prompt as in step 3. Fetch via fetch_assets.yml, frame-audit vs checklist.
   Fail -> fix masters, repeat. Pass -> step 3.
3. FLEET: for i in 0..27, alternating (even i -> new A master job id, odd i -> new B
   master job id), duration 15 (i<26), 8 (i=26), 9 (i=27):
   generate_video seedance_2_0: prompt "Re-render the reference video's woman - SAME
   real woman, identical face, identical motion and lip movements frame-for-frame - now
   seated in the wooden chair of the reference image's wood-paneled study, matching its
   exact cinematic lighting, camera quality, framing and grain. Her legs stay still and
   crossed. Change nothing about her identity or performance." 1080p, std,
   generate_audio false, declined_preset_id 24bae836-2c4a-48e0-89b6-49fcc0b21612.
   NOTE: max 8 parallel; submit in waves as slots free (429 = wait).
   Skip canary chunks already rendered (4,5) - reuse their results.
4. ASSEMBLE: collect all rawUrls in chunk order -> dispatch workflow
   assemble_seedance.yml (ref main) inputs: urls_json = JSON array of 28 URLs,
   out_name Courtney_CINEMA_FINAL_0717 (replaces file on page automatically).
5. AUDIT (holistic, client-mandated): pull deliverables/qc_cinema/*.jpg; check per
   frame: chair snug+back against backrest+no side gap; framing wide per spec; real
   her; limbs whole; seams; lip-sync spot check incl. t=400 tail; overall "production
   real" read. Fix failures via targeted chunk re-render (retake budget) before
   announcing. Then deliver page link + audit verdict.

## Infra reminders
- Shell egress proxied; cloudfront/drive/wetransfer BLOCKED locally; use GitHub
  workflows (fetch_assets.yml, wetransfer_chunks.yml, upload_put.yml) as relays.
  media.githubusercontent.com + raw.githubusercontent.com are shell-accessible.
- Page: https://gitteromri-ux.github.io/lla-s09-s10-downloads/
- Timeline promise: ~95 min machine time total. Client presents ~3h from GO
  (given ~19:30-20:00 UTC July 19). Report slips immediately, relative times only.
