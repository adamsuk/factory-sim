import React from "react";
import { createRoot } from "react-dom/client";
import FactorySim from "../src/FactorySim";

const sourceRef = (window as unknown as { FACTORY_SIM_REF?: string }).FACTORY_SIM_REF || "main";
const root = document.getElementById("root");
if (!root) throw new Error("missing root");
createRoot(root).render(
  <React.StrictMode>
    <main className="mx-auto max-w-4xl p-6">
      <p className="mb-4 text-sm text-gray-500">Release test for {sourceRef}. This page loads src/ from that ref.</p>
      <FactorySim sourceRef={sourceRef} />
    </main>
  </React.StrictMode>,
);
