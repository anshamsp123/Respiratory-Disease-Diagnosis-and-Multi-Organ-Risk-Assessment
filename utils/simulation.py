import numpy as np # Reload trigger: 2026-05-04 00:53
import pandas as pd
import random
import matplotlib.pyplot as plt
import io

def generate_risk_timeline_chart(current_kidney, current_heart):
    days = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5\n(Current)']
    
    def simulate_trend(current_val):
        trend = []
        val = current_val
        for _ in range(4):
            val = max(0, min(100, val + random.uniform(-10, 15)))
            trend.insert(0, val)
        trend.append(current_val)
        return trend

    kidney_trend = simulate_trend(current_kidney)
    heart_trend = simulate_trend(current_heart)
    
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(7, 4), dpi=300)
    
    ax.plot(days, kidney_trend, marker='o', linewidth=2.5, markersize=8, color='#f59e0b', label='Kidney Risk %')
    ax.plot(days, heart_trend, marker='o', linewidth=2.5, markersize=8, color='#ef4444', label='Heart Risk %')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#dddddd')
    ax.spines['bottom'].set_color('#dddddd')
    
    ax.yaxis.grid(True, linestyle='--', alpha=0.6)
    
    ax.set_ylim(0, 105)
    ax.set_ylabel('Risk Level (%)', fontsize=11, color='#4b5563')
    ax.legend(loc='upper left', frameon=False, fontsize=10)
    
    plt.xticks(fontsize=10, color='#4b5563')
    plt.yticks(fontsize=10, color='#4b5563')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_contribution_pie_chart():
    labels = ['Image Model', 'Clinical Data', 'Demographics']
    image_contrib = random.uniform(50, 60)
    clinical_contrib = random.uniform(30, 40)
    demographics_contrib = 100 - image_contrib - clinical_contrib
    sizes = [image_contrib, clinical_contrib, demographics_contrib]
    colors = ['#3b82f6', '#f59e0b', '#10b981']
    
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(5, 5), dpi=300)
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                      startangle=90, colors=colors, 
                                      textprops={'fontsize': 11, 'color': '#374151'}, 
                                      wedgeprops={'edgecolor': 'white', 'linewidth': 2})
                                      
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_weight('bold')
        
    ax.axis('equal') 
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    buf.seek(0)
    plt.close(fig)
    return buf
