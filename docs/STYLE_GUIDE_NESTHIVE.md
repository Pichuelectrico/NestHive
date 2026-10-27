# NestHive — guía visual MVP

## Tema MVP: Café & Amarillo

La interfaz se lee como café profundo + amarillo miel + crema. El rojo queda reservado para semántica operativa (por ejemplo AGV Nestlé, alarmas y errores), nunca como decoración.

| Token | Hex | Uso |
|---|---|---|
| `--hive-miel` | `#F9AE08` | marca, CTA primario, acentos de navegación |
| `--hive-cacao` | `#5B3918` | logotipo, títulos y contraste de marca |
| `--hive-crema` | `#FBFBF8` | superficies limpias y fondos de contenido |
| `--hive-arena` | `#EAD3A9` | fondos suaves, separadores y contexto |
| `--hive-oro-claro` | `#FBC866` | hover, highlights y estados de atención no críticos |
| `--nh-cocoa-deep` | `#241609` | canvas y superficies oscuras |
| `--nh-cocoa` | `#3B2413` | paneles elevados |

## Reglas de aplicación

- La identidad NestHive usa miel + cacao; no usar rojo como color de marca.
- Aplicar 60/30/10: crema/café base, cacao en superficies y miel como acento; rojo solo semántico.
- Rojo, verde y ámbar semánticos se conservan para estados operativos, alertas y salud de flota. No recolorear AMRs ni estados del mapa.
- Fondos: café profundo en el canvas; crema para tarjetas y texto; paneles elevados cacao con bordes café.
- Contraste: cacao sobre crema/miel; texto blanco solo sobre cacao suficientemente oscuro.
- El header muestra el monograma `NH` en miel con texto cacao y el nombre NestHive.

## Mapping para slides

- Portada y propuesta: cacao para titulares, miel para la palabra Hive y cifras clave.
- Demo: canvas café, cuadrícula/edges arena con baja opacidad, nodos crema/miel; mantener colores funcionales de flota y usar miel en foco.
- Arquitectura/Wi‑Fi: crema como fondo, arena para capas, cacao para etiquetas.
- Inversión/ROI: miel para CAPEX/piloto, cacao para valores y líneas de lectura.
- Sostenibilidad/ODS: conservar el color oficial del ODS cuando aplique; NestHive no debe competir con ese código.
- Q&A y apéndices: jerarquía neutra, acentos miel puntuales.

## Tokens CSS

Los tokens viven en `frontend/app/globals.css` como `--hive-miel`, `--hive-cacao`, `--hive-crema`, `--hive-arena` y `--hive-oro-claro`. `--nest-accent` apunta a miel; `--nest-red` permanece reservado para semántica operativa.
