# STEM SEPARATION AUDIT — fa_philippe_clip.mp4

Method: Demucs htdemucs, two-stem (vocals / no_vocals), CPU.

## Levels
- fa_music_clean.m4a — mean -25.0 dB, max -7.8 dB
- fa_voice_only.m4a — mean -25.2 dB, max -5.0 dB
- fa_music_bed_long.m4a — mean -24.9 dB, max -7.8 dB

## Residual-speech check (whisper-tiny fr on each stem)
- MUSIC stem transcription: "Sous-sous-sous. ..."
- VOICE stem transcription: "en France, les refinement sont vraiment dans les contextes. Au revoir du sein de la borde d'Ovignat, pour le projés artiste de multiples mille, l'anguage vollos culture. Dans la France, le sauveure de 20e sessions vous le connaissez en toute ville et de confidence aux deux autres élegants d'inés, et les voies, des élegants d'éteils, et des anti-léans de se passeurs. L'élegance and corpse, yours, t"

PASS criterion: music stem transcription empty or gibberish fragments only;
voice stem carries the full French VO.
