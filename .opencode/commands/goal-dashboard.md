---
description: Abre la Torre de Control de Goal (objetivos) y la pestaña Auto-research (pruebas, gráfica y cuadernos)
---

Abre la Torre de Control del proyecto actual:

1. Lanza en segundo plano, desde la raíz del proyecto: `python "$HOME/.config/opencode/skills/goal/dashboard/torre.py" --serve --port 3010 --project "<raíz del proyecto>"`
2. Comprueba que responde y abre `http://127.0.0.1:3010` en el navegador.
3. Responde con la URL y 1 línea de qué se ve. Si el puerto está ocupado, usa 3011 y avísalo.

La página se regenera en cada visita: enseña el avance mientras Goal trabaja. La pestaña Auto-research lista cada investigación, con gráfica de progreso arriba y las pruebas debajo; cada prueba abre su cuaderno completo.
