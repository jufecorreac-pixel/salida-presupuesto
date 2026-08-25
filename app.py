# -*- coding: utf-8 -*-
"""Interfaz para armar el presupuesto de la salida y repartirlo entre dos."""

import os

import pandas as pd
import streamlit as st

from presupuesto_data import (
    HOSPEDAJE_MAX,
    HOSPEDAJE_PASO,
    RUTA_EXCEL,
    cargar_hospedajes,
    cargar_presupuesto,
    cop,
    guardar_hospedajes,
)

PERSONA_A = "Juan Fernando"
PERSONA_B = "Gabriela"

st.set_page_config(page_title="Salida - Presupuesto", page_icon="🚗", layout="wide")


@st.cache_data
def _presupuesto(_mtime):
    # _mtime entra solo para invalidar el cache cuando se edita el Excel.
    return cargar_presupuesto()


def presupuesto():
    return _presupuesto(os.path.getmtime(RUTA_EXCEL))


def tabla_items(items):
    """DataFrame de items listo para mostrar."""
    return pd.DataFrame(
        [
            {"Producto": i["producto"], "Cantidad": i["cantidad"], "Precio": cop(i["precio"])}
            for i in items
        ]
    )


datos = presupuesto()

st.title("🚗 Salida - Presupuesto")
st.caption(
    "Los precios salen de Presupuesto.xlsx. Escoge las opciones y mira cuánto paga cada uno."
)

tab_presupuesto, tab_mercado, tab_airbnb = st.tabs(
    ["Presupuesto", "Lista de mercado", "Airbnb"]
)

with tab_presupuesto:
    col_sel, col_res = st.columns([1.1, 1], gap="large")

    # ------------------------------------------------------------------ seleccion
    with col_sel:
        st.subheader("Hospedaje")
        hospedaje = st.slider(
            "Valor del hospedaje",
            min_value=0,
            max_value=HOSPEDAJE_MAX,
            value=0,
            step=HOSPEDAJE_PASO,
            label_visibility="collapsed",
        )
        st.markdown("### " + cop(hospedaje))
        st.caption(
            "Arrastra hasta el valor del Airbnb. Tope {} · en el Excel figura {}.".format(
                cop(HOSPEDAJE_MAX), cop(datos["hospedaje_ref"])
            )
        )

        airbnbs = cargar_hospedajes()
        if airbnbs:
            st.write("**Opciones de Airbnb**")
            for i, a in enumerate(airbnbs):
                c1, c2 = st.columns([2, 1])
                c1.write(a["nombre"] or "Airbnb {}".format(i + 1))
                if a["url"]:
                    c2.link_button("Ver en Airbnb", a["url"], use_container_width=True)
                else:
                    c2.caption("sin link")
        else:
            st.info("Aún no hay links cargados - agrégalos en la pestaña **Airbnb**.")

        st.divider()

        st.subheader("Desayunos (2 días)")
        desayunos = datos["desayunos"]
        st.caption(
            "Los desayunos son fijos, no se escogen. Total: **{}**".format(
                cop(desayunos["total"])
            )
        )
        with st.expander("Ver qué incluye"):
            st.dataframe(
                tabla_items(desayunos["items"]), hide_index=True, use_container_width=True
            )

        st.divider()

        st.subheader("Almuerzo")
        almuerzos = datos["almuerzos"]
        idx_almuerzo = st.radio(
            "Escoge un almuerzo",
            options=range(len(almuerzos)),
            format_func=lambda i: "{} - {}".format(
                almuerzos[i]["nombre"], cop(almuerzos[i]["total"])
            ),
            label_visibility="collapsed",
        )
        almuerzo = almuerzos[idx_almuerzo]
        with st.expander("Ver qué incluye"):
            st.dataframe(
                tabla_items(almuerzo["items"]), hide_index=True, use_container_width=True
            )

        st.divider()

        st.subheader("Cenas")
        cenas = datos["cenas"]

        def etiqueta_cena(i):
            return "{} - {}".format(cenas[i]["nombre"], cop(cenas[i]["total"]))

        c1, c2 = st.columns(2)
        idx_cena1 = c1.selectbox(
            "Cena 1", options=range(len(cenas)), format_func=etiqueta_cena, index=0
        )
        idx_cena2 = c2.selectbox(
            "Cena 2",
            options=range(len(cenas)),
            format_func=etiqueta_cena,
            index=min(1, len(cenas) - 1),
        )
        cena1, cena2 = cenas[idx_cena1], cenas[idx_cena2]
        if idx_cena1 == idx_cena2:
            st.caption("Escogiste la misma cena las dos noches: se cuenta doble.")
        with st.expander("Ver qué incluyen"):
            st.write("**Cena 1 - {}**".format(cena1["nombre"]))
            st.dataframe(tabla_items(cena1["items"]), hide_index=True, use_container_width=True)
            st.write("**Cena 2 - {}**".format(cena2["nombre"]))
            st.dataframe(tabla_items(cena2["items"]), hide_index=True, use_container_width=True)

        st.divider()

        st.subheader("Carro")
        lavada = datos["lavada"]
        con_lavada = st.checkbox(
            "{} (+{})".format(lavada["nombre"], cop(lavada["total"])), value=False
        )

    # ------------------------------------------------------------------- resultado
    with col_res:
        st.subheader("Desglose")

        rubros = [
            ("Hospedaje", "Airbnb" if hospedaje else "sin definir", hospedaje),
            ("Desayunos (2 días)", "fijo", desayunos["total"]),
            ("Almuerzo", almuerzo["nombre"], almuerzo["total"]),
            ("Cena 1", cena1["nombre"], cena1["total"]),
            ("Cena 2", cena2["nombre"], cena2["total"]),
            (
                "Lavada de carro",
                "incluida" if con_lavada else "no incluida",
                lavada["total"] if con_lavada else 0,
            ),
        ]
        total = sum(r[2] for r in rubros)

        df_rubros = pd.DataFrame(
            [{"Rubro": r[0], "Opción": r[1], "Valor": cop(r[2])} for r in rubros]
        )
        # Los rubros en cero se ven en gris para distinguirlos de un vistazo.
        grises = ["color: gray" if r[2] == 0 else "" for r in rubros]
        estilo = df_rubros.style.apply(lambda _col: grises, axis=0)
        st.dataframe(estilo, hide_index=True, use_container_width=True)

        st.metric("TOTAL SALIDA", cop(total))

        st.divider()
        st.subheader("¿Cómo se divide?")

        pct_a = st.slider("% que paga {}".format(PERSONA_A), 0, 100, 50, step=5)
        pct_b = 100 - pct_a
        # Solo se redondea una parte: asi la suma da el total exacto, sin sobrar un peso.
        paga_a = round(total * pct_a / 100)
        paga_b = total - paga_a

        st.progress(pct_a / 100)
        m1, m2 = st.columns(2)
        m1.metric(PERSONA_A, cop(paga_a), "{}%".format(pct_a), delta_color="off")
        m2.metric(PERSONA_B, cop(paga_b), "{}%".format(pct_b), delta_color="off")

        resumen = ["SALIDA - PRESUPUESTO", ""]
        for nombre_rubro, opcion, valor in rubros:
            resumen.append("{:<22}{:<24}{}".format(nombre_rubro, opcion, cop(valor)))
        resumen += [
            "",
            "{:<46}{}".format("TOTAL", cop(total)),
            "",
            "{} ({}%): {}".format(PERSONA_A, pct_a, cop(paga_a)),
            "{} ({}%): {}".format(PERSONA_B, pct_b, cop(paga_b)),
        ]
        st.download_button(
            "Descargar resumen",
            data="\n".join(resumen).encode("utf-8"),
            file_name="resumen_salida.txt",
            mime="text/plain",
        )

# ---------------------------------------------------------------- lista de mercado
with tab_mercado:
    st.subheader("Lista de mercado")
    st.caption(
        "Todo lo que hay que comprar según lo que escogiste "
        "(el hospedaje y la lavada no entran aquí)."
    )

    # Un mismo producto puede venir de varias comidas: se agrupa y se suma.
    consolidado = {}
    for bloque in (desayunos, almuerzo, cena1, cena2):
        for item in bloque["items"]:
            clave = item["producto"].strip().lower()
            if clave in consolidado:
                consolidado[clave]["precio"] += item["precio"]
                consolidado[clave]["veces"] += 1
                if item["cantidad"] and item["cantidad"] not in consolidado[clave]["cantidades"]:
                    consolidado[clave]["cantidades"].append(item["cantidad"])
            else:
                consolidado[clave] = {
                    "producto": item["producto"],
                    "cantidades": [item["cantidad"]] if item["cantidad"] else [],
                    "precio": item["precio"],
                    "veces": 1,
                }

    filas = []
    for v in consolidado.values():
        cantidad = " + ".join(v["cantidades"])
        if v["veces"] > 1:
            cantidad = "{}  (x{})".format(cantidad, v["veces"])
        filas.append(
            {"Producto": v["producto"], "Cantidad": cantidad, "Precio": cop(v["precio"])}
        )

    st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
    st.metric("Total mercado", cop(sum(v["precio"] for v in consolidado.values())))

# ------------------------------------------------------------------------- airbnb
with tab_airbnb:
    st.subheader("Links de Airbnb")
    st.caption(
        "Agrega, edita o borra opciones de hospedaje. Solo son enlaces: no suman al total, "
        "el valor del hospedaje lo pone la barra."
    )
    st.warning(
        "En la versión publicada en internet estos cambios se pierden cuando la app se "
        "reinicia. Para que queden fijos hay que guardarlos en el archivo hospedajes.json "
        "del repositorio.",
        icon="⚠️",
    )

    actuales = cargar_hospedajes()
    base = pd.DataFrame(actuales if actuales else [{"nombre": "", "url": ""}])
    editado = st.data_editor(
        base,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "nombre": st.column_config.TextColumn("Nombre", width="medium"),
            "url": st.column_config.LinkColumn("Link de Airbnb", width="large"),
        },
        key="editor_airbnb",
    )

    if st.button("Guardar cambios", type="primary"):
        guardados = guardar_hospedajes(editado.to_dict("records"))
        st.success("Guardados {} hospedajes.".format(len(guardados)))
        st.rerun()
