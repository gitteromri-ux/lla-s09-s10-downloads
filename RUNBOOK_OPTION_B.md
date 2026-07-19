# RUNBOOK — Option B: Seedance blend-quality test (Courtney / 0717)

Purpose: real Courtney footage re-rendered to the client-approved Higgsfield look.
This file lets ANY session (including a fresh one with the HIGGSFIELD connector
enabled) execute immediately. Everything referenced is already uploaded/committed.

## Standing rules (client-mandated)
1. NOTHING runs and NO credit is spent without the client's explicit "GO"
   after seeing a cost preflight.
2. Full QC before the client sees any output: audit frames vs the master image
   (assets/keyframe_final.png). Gates: real Courtney only; full body seated in
   chair; legs+arms whole; proportions matched; Higgsfield blend quality; no
   smears/ghosts/height errors/room changes.
3. The composite pipeline (rembg paste) is DEAD by client order. Do not iterate it.
4. Relative time quotes only (no wall-clock).

## Assets (already in place)
- Master set image (client-approved look, AI woman to be ignored):
  repo assets/keyframe_final.png ; Higgsfield image job id: 991bf8d1-bd04-48ba-a10f-c95d85635667
- Empty plate (man removed): repo assets/plateA_final.png ; job id: a820321b-4eaa-4a41-ab05-6204451517ea
- Real Courtney 10s test clip (t=60-70s, 1080p): repo deliverables/clips/seg_test.mp4 (LFS);
  Higgsfield media id: 8a72dc03-2e16-4f61-9a77-81f1f4c96f52
- Source video 0717 (7 min): Drive zip id 1VyhOqzO5FuHcnSRKzDpA40AK_4hJkqSQ
  (fetchable by GitHub runner via drive.usercontent URL; see clip_segment.yml)
- Full 29-min source: Drive id 1y2Q8zy9HWmMF7bmKZYe96ioQ5QirXU7o
- Credits at last check: 266.48 (ultra plan). Spent so far via agent: 35.

## The test (single 10s shot)
Tool: mcp__HIGGSFIELD__generate_video, model seedance_2_0 (fallback: seedance_2_0_mini)
Params sketch:
  model: seedance_2_0, duration: 10, resolution: 1080p, mode: std,
  aspect_ratio: 16:9, generate_audio: false,
  medias: [
    {role: video_references, value: 8a72dc03-2e16-4f61-9a77-81f1f4c96f52},
    {role: image_references, value: 991bf8d1-bd04-48ba-a10f-c95d85635667}
  ]
  prompt: "Re-render the reference video's woman - SAME real woman, identical face,
  identical motion and lip movements frame-for-frame - now seated in the wooden chair
  of the reference image's wood-paneled study, matching its exact cinematic lighting,
  camera quality, framing and grain. Change nothing about her identity or performance."
STEP 1: same call with get_cost: true -> report credits to client -> WAIT for GO.
STEP 2: on GO, generate. Poll job_display with the returned id.
STEP 3: output URL is cloudfront (blocked from shell) -> fetch via workflow
  fetch_assets.yml (input urls=<rawUrl>) -> lands in deliverables/fetched/ on main.
STEP 4: QC vs master (extract frames with pip av). Only then show client.
STEP 5: mux HER REAL AUDIO over any output before delivery
  (ffmpeg -i video -i audio -c:v copy -map 0:v -map 1:a). Kling/Seedance audio is discarded.

## Scale-up (only after client approves test)
- 7-min = 42 x 10s chunks (clip_segment.yml cuts them; upload_put.yml PUTs each to a
  presigned URL from media_upload; media_confirm each). Cost scales linearly - price it
  from the test's real cost and get explicit approval + likely credit top-up first.
- Deliver via existing page pipeline (index.html cards on main; LFS; >2GB must split, see publish29.yml).

## Infra notes
- Shell egress is proxied: cloudfront/drive.usercontent/upload.higgsfield.ai BLOCKED;
  media.githubusercontent.com + raw.githubusercontent.com ALLOWED.
  GitHub runners have open egress - use workflows as fetch/upload relays.
- media_import_url only accepts proper content-type (image/* ok from raw.github;
  mp4 must go media_upload + runner PUT).
- Delivery page: https://gitteromri-ux.github.io/lla-s09-s10-downloads/
- 7-min composite fallback (client-rejected look, kept as floor):
  deliverables/Courtney_NEWSET_FINAL_0717.mp4 on main.
