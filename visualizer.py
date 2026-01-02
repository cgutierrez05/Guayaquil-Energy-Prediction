import matplotlib.pyplot as plt

def graficar_comparativa(df_model, df_bnee):
    print(">>> Generando gráfico... (Mira tu barra de tareas si no aparece)")
    
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Eje 1: Consumo GYE
    ax1.set_xlabel('Fecha')
    ax1.set_ylabel('Consumo GYE Estimado (MWh)', color='tab:blue', fontsize=12, fontweight='bold')
    ax1.plot(df_model.index, df_model['consumo_mwh'], color='tab:blue', linewidth=2, marker='o', label='Demanda GYE (Corregida)')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Eje 2: Producción Nacional
    ax2 = ax1.twinx()
    ax2.set_ylabel('Producción Nacional (GWh)', color='tab:orange', fontsize=12, fontweight='bold')
    
    # Filtramos BNEE
    bnee_subset = df_bnee[df_bnee.index.isin(df_model.index)]
    ax2.plot(bnee_subset.index, bnee_subset['prod_total_gwh'], color='tab:orange', linestyle='--', alpha=0.7, label='Producción Nacional')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    plt.title('Modelo de Demanda Eléctrica: Guayaquil vs Nacional', fontsize=14)
    plt.grid(True, linestyle=':', alpha=0.6)
    fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))
    plt.tight_layout()
    
    # --- CAMBIO CLAVE AQUÍ ---
    # block=True obliga a Python a esperar que cierres la ventana
    plt.show(block=True)