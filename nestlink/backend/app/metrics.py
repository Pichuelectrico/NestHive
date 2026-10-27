# app/metrics.py
# Gestión y cálculo de KPIs y métricas de ROI para NestLink

from app.models import KPIsState

class KPIManager:
    def __init__(self):
        self.viajes_completados: int = 0
        self.viajes_vacios_evitados: int = 0
        self.paradas_evitadas: int = 0
        self.total_delivery_time_min: float = 0.0
        self.km_evitados: float = 0.0
        self.total_km_recorridos: float = 0.0
        # KPI "tiempo en OUT" (pre-entrega exclusiva): suma en segundos de la espera de cada
        # paquete en el buffer OUT (arribo → entrega en el muro) y nº de paquetes medidos.
        self.total_out_wait_sec: float = 0.0
        self.out_pkgs_measured: int = 0

    def record_trip_completed(self, duration_min: float, distance_km: float, was_empty_prevented: bool = False):
        self.viajes_completados += 1
        self.total_delivery_time_min += duration_min
        self.total_km_recorridos += distance_km
        if was_empty_prevented:
            self.viajes_vacios_evitados += 1
            self.km_evitados += distance_km * 0.45

    def record_stoppage_prevented(self):
        self.paradas_evitadas += 1

    def record_out_wait_sec(self, wait_sec: float):
        """Registra el tiempo (en segundos) que un paquete estuvo esperando en un OUT
        antes de la entrega exclusiva al muro. Se agrega al KPI 'tiempo medio en OUT'."""
        self.total_out_wait_sec += max(0.0, wait_sec)
        self.out_pkgs_measured += 1

    def get_snapshot(self) -> KPIsState:
        avg_time = (
            round(self.total_delivery_time_min / self.viajes_completados, 2)
            if self.viajes_completados > 0
            else 2.1
        )
        # KPI "tiempo medio en OUT": promedio de la espera de los paquetes (arribo→entrega al muro)
        avg_out_wait_min = (
            round(self.total_out_wait_sec / self.out_pkgs_measured / 60.0, 2)
            if self.out_pkgs_measured > 0
            else 0.0
        )
        # ROI de km evitados vs recorridos
        total = self.total_km_recorridos + self.km_evitados
        roi_pct = round((self.km_evitados / max(total, 0.1)) * 100.0, 1) if total > 0 else 32.5

        return KPIsState(
            viajes_completados=self.viajes_completados,
            viajes_vacios_evitados=self.viajes_vacios_evitados,
            paradas_evitadas=self.paradas_evitadas,
            tiempo_medio_entrega_min=avg_time,
            km_evitados=round(self.km_evitados, 2),
            roi_km_pct=roi_pct,
            tiempo_medio_en_out_min=avg_out_wait_min
        )
