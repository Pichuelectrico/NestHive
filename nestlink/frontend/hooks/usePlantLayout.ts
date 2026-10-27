"use client";

import { useCallback, useEffect, useState } from "react";
import { DEFAULT_PLANT_ID, DEFAULT_PLANT_NAME } from "@/lib/config";
import { fetchLayout, fetchPlants, selectPlant } from "@/lib/api";
import type { PlantInfo, PlantLayout } from "@/lib/types";

export function usePlantLayout() {
  const [plants, setPlants] = useState<PlantInfo[]>([]);
  const [selectedPlantId, setSelectedPlantId] = useState(DEFAULT_PLANT_ID);
  const [layout, setLayout] = useState<PlantLayout | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [layoutKey, setLayoutKey] = useState(0);

  useEffect(() => {
    fetchPlants().then(setPlants).catch(() => {
      setPlants([{ id: DEFAULT_PLANT_ID, nombre: DEFAULT_PLANT_NAME }]);
    });
  }, []);

  const loadLayout = useCallback(async (plantId: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchLayout(plantId);
      setLayout(data);
      setLayoutKey((k) => k + 1);
    } catch (e) {
      setError(String(e));
      setLayout(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadLayout(selectedPlantId);
  }, [selectedPlantId, loadLayout]);

  const changePlant = useCallback(
    async (plantId: string) => {
      if (plantId === selectedPlantId) return;
      setSelectedPlantId(plantId);
      try {
        await selectPlant(plantId);
      } catch {
        // offline: seguir con layout local si existe
      }
      await loadLayout(plantId);
    },
    [selectedPlantId, loadLayout]
  );

  const selectedPlant =
    plants.find((p) => p.id === selectedPlantId) ??
    ({ id: selectedPlantId, nombre: selectedPlantId } as PlantInfo);

  return {
    plants,
    selectedPlant,
    selectedPlantId,
    changePlant,
    layout,
    layoutKey,
    error,
    loading,
  };
}
