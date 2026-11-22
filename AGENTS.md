# session-focus

Taller del canal de YouTube **Lamplight Sessions** (@Lamplight-sessions) (vídeos de estudio con Escena en bucle y música lofi generadas con IA). El vocabulario está en `GLOSSARY.md`; úsalo al hablar con el usuario y al escribir en el repo. El usuario escribe en español; los prompts y los metadatos de YouTube van en inglés.

## Trabajo con Sesiones

- Registro, estados y rutas de `media/`: `docs/sesiones.md`.
- Identidad visual y cómo escribir prompts de imagen, Bucle, Pistas y metadatos: `docs/hilo-conductor.md`.
- Flujo completo: skills `/nueva-sesion` y `/montaje`.
- `scripts/generar.py` gasta dinero de la cuenta del usuario: lánzalo con `--si` solo tras enseñarle el coste estimado y recibir su aprobación para esa ejecución.

## Agent skills

### Issue tracker

Issues are tracked in this repo's GitHub Issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default triage vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
