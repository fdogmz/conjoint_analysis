from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm

# Wrapper ligero para cache de Streamlit.
try:
    import streamlit as st

    st_cache_data = st.cache_data
except Exception:  # pragma: no cover
    def st_cache_data(func):
        return func


ATTRIBUTES: Dict[str, List[str]] = {
    "Marca": ["Alpha", "Beta", "Gamma"],
    "Precio": ["Bajo", "Medio", "Alto"],
    "Capacidad": ["64GB", "128GB", "256GB"],
}


def build_profiles(design: str = "fractional") -> pd.DataFrame:
    if design == "full":
        profiles = pd.MultiIndex.from_product(
            [ATTRIBUTES["Marca"], ATTRIBUTES["Precio"], ATTRIBUTES["Capacidad"]],
            names=["Marca", "Precio", "Capacidad"],
        ).to_frame(index=False)
    else:
        # Arreglo ortogonal L9 para 3 atributos con 3 niveles (main effects).
        l9_rows = [
            (0, 0, 0),
            (0, 1, 1),
            (0, 2, 2),
            (1, 0, 1),
            (1, 1, 2),
            (1, 2, 0),
            (2, 0, 2),
            (2, 1, 0),
            (2, 2, 1),
        ]
        profiles = pd.DataFrame(
            {
                "Marca": [ATTRIBUTES["Marca"][r[0]] for r in l9_rows],
                "Precio": [ATTRIBUTES["Precio"][r[1]] for r in l9_rows],
                "Capacidad": [ATTRIBUTES["Capacidad"][r[2]] for r in l9_rows],
            }
        )

    profiles["PerfilID"] = np.arange(1, len(profiles) + 1)
    return profiles


@st_cache_data
def generate_synthetic_dataset(
    n_respondents: int = 40, seed: int = 42, design: str = "fractional"
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    profiles = build_profiles(design=design)

    base_partworths = {
        "Marca": {"Alpha": 0.9, "Beta": 0.4, "Gamma": 0.0},
        "Precio": {"Bajo": 1.1, "Medio": 0.4, "Alto": 0.0},
        "Capacidad": {"64GB": 0.0, "128GB": 0.5, "256GB": 1.0},
    }

    rows = []
    for rid in range(1, n_respondents + 1):
        alpha_shift = rng.normal(0.0, 0.25)
        beta_shift = rng.normal(0.0, 0.25)
        gamma_shift = rng.normal(0.0, 0.25)
        low_shift = rng.normal(0.0, 0.2)
        med_shift = rng.normal(0.0, 0.2)
        high_shift = rng.normal(0.0, 0.2)
        c64_shift = rng.normal(0.0, 0.15)
        c128_shift = rng.normal(0.0, 0.15)
        c256_shift = rng.normal(0.0, 0.15)

        respondent_pw = {
            "Marca": {
                "Alpha": base_partworths["Marca"]["Alpha"] + alpha_shift,
                "Beta": base_partworths["Marca"]["Beta"] + beta_shift,
                "Gamma": base_partworths["Marca"]["Gamma"] + gamma_shift,
            },
            "Precio": {
                "Bajo": base_partworths["Precio"]["Bajo"] + low_shift,
                "Medio": base_partworths["Precio"]["Medio"] + med_shift,
                "Alto": base_partworths["Precio"]["Alto"] + high_shift,
            },
            "Capacidad": {
                "64GB": base_partworths["Capacidad"]["64GB"] + c64_shift,
                "128GB": base_partworths["Capacidad"]["128GB"] + c128_shift,
                "256GB": base_partworths["Capacidad"]["256GB"] + c256_shift,
            },
        }

        intercept = 4.0 + rng.normal(0, 0.3)

        for _, p in profiles.iterrows():
            utility = (
                intercept
                + respondent_pw["Marca"][p["Marca"]]
                + respondent_pw["Precio"][p["Precio"]]
                + respondent_pw["Capacidad"][p["Capacidad"]]
            )
            noisy_rating = utility + rng.normal(0, 0.5)
            rating = float(np.clip(noisy_rating, 1, 10))

            rows.append(
                {
                    "RespondentID": rid,
                    "PerfilID": int(p["PerfilID"]),
                    "Marca": p["Marca"],
                    "Precio": p["Precio"],
                    "Capacidad": p["Capacidad"],
                    "Rating": round(rating, 2),
                }
            )

    return pd.DataFrame(rows)


def _dummy_design(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    categorical_cols = ["Marca", "Precio", "Capacidad"]
    X = pd.get_dummies(df[categorical_cols], drop_first=True, dtype=float)
    X = sm.add_constant(X, has_constant="add")
    return X, categorical_cols


def fit_respondent_ols(df_resp: pd.DataFrame):
    if df_resp["Rating"].nunique() <= 1:
        raise ValueError("El encuestado tiene ratings constantes; OLS no es identificable.")

    X, categorical_cols = _dummy_design(df_resp)
    y = df_resp["Rating"].astype(float)

    model = sm.OLS(y, X).fit()

    partworths = {}
    for attr in categorical_cols:
        levels = sorted(df_resp[attr].unique().tolist())
        attr_pw = {}
        base_level = levels[0]
        attr_pw[base_level] = 0.0
        for lvl in levels[1:]:
            coef_name = f"{attr}_{lvl}"
            attr_pw[lvl] = float(model.params.get(coef_name, 0.0))
        partworths[attr] = attr_pw

    return model, partworths


def relative_importance(partworths: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    ranges = {}
    for attr, level_map in partworths.items():
        vals = list(level_map.values())
        ranges[attr] = max(vals) - min(vals)

    total_range = sum(ranges.values())
    if total_range <= 0:
        out = {k: 0.0 for k in ranges}
    else:
        out = {k: (v / total_range) * 100 for k, v in ranges.items()}

    return pd.DataFrame(
        {"Atributo": list(out.keys()), "ImportanciaRelativa": list(out.values())}
    )


def utility_for_profile(
    profile: Dict[str, str],
    model_params: pd.Series,
    attribute_levels: Dict[str, List[str]],
) -> float:
    total = float(model_params.get("const", 0.0))

    for attr, selected_level in profile.items():
        base_level = sorted(attribute_levels[attr])[0]
        if selected_level == base_level:
            continue
        coef_name = f"{attr}_{selected_level}"
        total += float(model_params.get(coef_name, 0.0))

    return total


def first_choice_share(utility_df: pd.DataFrame) -> pd.Series:
    # Si hay empate, se divide el voto entre productos empatados.
    shares = pd.Series(0.0, index=utility_df.columns)
    for _, row in utility_df.iterrows():
        max_u = row.max()
        winners = row[row == max_u].index.tolist()
        vote = 1.0 / len(winners)
        for w in winners:
            shares[w] += vote

    return (shares / len(utility_df)) * 100
