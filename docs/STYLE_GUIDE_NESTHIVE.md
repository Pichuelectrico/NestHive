# NestHive — guía visual MVP

## Paleta

| Token | Hex | Uso |
|---|---|---|
| `--hive-miel` | `#F9AE08` | marca, CTA primario, acentos de navegación |
| `--hive-cacao` | `#5B3918` | logotipo, títulos y contraste de marca |
| `--hive-crema` | `#FBFBF8` | superficies limpias y fondos de contenido |
| `--hive-arena` | `#EAD3A9` | fondos suaves, separadores y contexto |
| `--hive-oro-claro` | `#FBC866` | hover, highlights y estados de atención no críticos |

## Reglas de aplicación

- La identidad NestHive usa miel + cacao; no usar rojo como color de marca.
- Rojo, verde y ámbar semánticos se conservan para estados operativos, alertas y salud de flota. No recolorear AMRs ni estados del mapa.
- Fondos: crema/blanco; paneles con borde neutro y arena únicamente como lavado sutil.
- Contraste: cacao sobre crema/miel; texto blanco solo sobre cacao suficientemente oscuro.
- El header muestra el monograma `NH` en miel con texto cacao y el nombre NestHive.

## Mapping para slides

- Portada y propuesta: cacao para titulares, miel para la palabra Hive y cifras clave.
- Demo: mantener mapa y flota con sus colores funcionales; usar miel solo en llamadas a la acción y marcadores de foco.
- Arquitectura/Wi‑Fi: crema como fondo, arena para capas, cacao para etiquetas.
- Inversión/ROI: miel para CAPEX/piloto, cacao para valores y líneas de lectura.
- Sostenibilidad/ODS: conservar el color oficial del ODS cuando aplique; NestHive no debe competir con ese código.
- Q&A y apéndices: jerarquía neutra, acentos miel puntuales.

## Tokens CSS

Los tokens viven en `frontend/app/globals.css` como `--hive-miel`, `--hive-cacao`, `--hive-crema`, `--hive-arena` y `--hive-oro-claro`. `--nest-accent` apunta a miel; `--nest-red` permanece reservado para semántica operativa.
