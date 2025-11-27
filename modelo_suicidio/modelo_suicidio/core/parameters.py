from dataclasses import dataclass

@dataclass
class ModeloParametros:
    delta: float      # δ: tasa media de defunción total
    delta_s: float    # δ_s: tasa media de defunción por suicidio
    delta_n: float    # δ_n = δ - δ_s: tasa media de defunción no suicida
    m: float          # m: tasa global de tratamiento (media geométrica T/P)
    phi: float        # ϕ: proporción de T que termina en R (recuperados)
    psi: float        # ψ: proporción de P que está en S (susceptibles)
    theta: float      # θ: flujo desde P (vulnerable) hacia S
    rho: float        # ρ: tasa con la que T pasa a R
    beta: float       # β: proporción de entrada a T debida a influencia social
    gamma: float      # γ: factor de entrada a T por otras causas (no influencia)
