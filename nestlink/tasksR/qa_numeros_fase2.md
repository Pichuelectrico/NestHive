# QA de Consistencia de Números — Fase 2 (Loja)

> Verificación de que las cifras clave del pitch sean **idénticas y coherentes** en todos los materiales. Ejecutado por el lead con chequeo por script (25-oct). **Veredicto global: ✅ coherente** — sin discrepancias de valor; solo diferencias de formato/redacción, corregidas donde importaba.

## Matriz de cobertura (✓ = presente · · = no aplica/variante de formato)

| Cifra | Deck (13 slides) | Guion oral 2 | Q&A | Onboarding | Wi-Fi | Obsidian F2 |
|---|---|---|---|---|---|---|
| 1.035 movimientos/día | ✓ (lead) | ✓ | ✓ | ✓ | · | ✓ |
| 215 pallets salida/turno | ✓ | · | · | ✓ | · | ✓ |
| 131 pallets entrada/turno | · | · | · | ✓ | · | ✓ |
| Takt 132 s | · | · | ✓ | ✓ | · | ✓ |
| 6 AMRs (5+1 N+1) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 89/89 tests | ✓ | · | ✓ | ✓ | · | · |
| Techo 411 (+91 %) | ✓ (lead) | ✓ | ✓ | ✓ | · | ✓ |
| CAPEX ≈ $0,95M (0,7–1,3) | ✓ | ✓ | ✓ | ✓ | · | ✓ |
| Ahorro $0,21M/año (0,13–0,30) | ✓ | ✓ | ✓ | ✓ | · | ✓ |
| Payback 4,5 años / ≤3 (3 turnos) | ✓ | ✓ | ✓ | ✓ | · | ✓ |
| **Piloto $0,22M reversible <1 turno** | ✓ | ✓ | ✓ | ✓ | · | ✓ |
| Ciclo 146/158 s | ✓ (lead) | ✓ | ✓ | · | · | ✓ |
| Sakasegawa 13 s @53 % / 111 s @85 % | ✓ (lead) | ✓ | ✓ | · | · | ✓ |
| Exactitud ≥99,9 % | · | ✓ | ✓ | ✓ | · | ✓ |
| Disponibilidad ≥98 % | · | · | · | ✓ | · | · |
| Espera ≤30 s p95 | · | · | · | ✓ | · | ✓ |
| RSSI ≥ −65 dBm | ✓ | · | · | · | ✓ | · |
| km evitados 0,32 × 0,45 | ✓ | · | ✓ | · | · | · |

*Las celdas "·" son intencionales en la mayoría (el guion no repite fórmulas; el deck no necesita todos los KPIs). Las marcadas "(lead)" se añadieron en la corrección de hoy.*

## Hallazgos y acciones

| # | Hallazgo | Acción |
|---|---|---|
| 1 | El deck narraba "6 AMRs" **sin mostrar la matemática de dimensionamiento** que el guion cuenta (146–158 s, ×1,4, ÷0,75, Sakasegawa, techo 411) | ✅ Card "Flota dimensionada" (slide 3) actualizado con la matemática completa |
| 2 | El deck decía "215 pallets/día" (fase 1) en vez de "1.035 movimientos/día (215 por turno)" (fase 2) | ✅ Lead del slide 3 actualizado |
| 3 | "Disponibilidad ≥98 %" usaba "98 %" (con espacio) en unos docs y "98%" en otros | ℹ️ Mismo valor; formato unificado en [KPIs del pitch]. No afecta |
| 4 | El PDF de fase 2 (Nestle.pdf) y el HTML deck son **dos artefactos distintos** — el HTML ahora incluye las cifras clave del PDF (1.035, 215/turno, 411, Sakasegawa) | ✅ Alineados |
| 5 | Ninguna discrepancia de **valor** entre deck ↔ guion ↔ Q&A ↔ onboarding ↔ Obsidian | — |

## Los 10 números canónicos (única fuente: citar estos)

1. **1.035** movimientos/día · 2. **215 / 131** pallets salida/entrada por turno · 3. **takt 132 s** · 4. **6 AMRs** (5+1 N+1, MiR1200) · 5. **89/89 tests** · 6. **techo 411 pallets/turno (+91 %)** · 7. **CAPEX ≈ $0,95M** · 8. **ahorro ≈ $0,21M/año** · 9. **payback 4,5 años (≤3 en 3 turnos)** · 10. **piloto $0,22M reversible <1 turno**

> 🔒 Documento **local** — no subir a GitHub (regla fase 2).
