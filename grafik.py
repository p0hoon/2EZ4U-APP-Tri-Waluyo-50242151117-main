# generate_grafik.py
# Menghasilkan file gambar SVG grafik perbandingan Insertion Sort vs Merge Sort

def buat_grafik_svg():
    width = 850
    height = 520
    margin_l = 90
    margin_r = 50
    margin_t = 60
    margin_b = 80

    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b

    # Data titik n dan jumlah perbandingan
    n_vals = [500, 1000, 2000, 4000]
    ins_vals = [61420, 246310, 985440, 3941820]
    mrg_vals = [3842, 8694, 19380, 42760]

    max_n = 4000
    max_comp = 4200000

    def map_x(n):
        return margin_l + (n / max_n) * plot_w

    def map_y(val):
        return margin_t + plot_h - (val / max_comp) * plot_h

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="background-color:#ffffff; font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif;">')

    # Judul Grafik
    svg.append(f'<text x="{width/2}" y="35" text-anchor="middle" font-size="18" font-weight="bold" fill="#1b2a32">Grafik Perbandingan: Ukuran Data (n) vs Jumlah Perbandingan</text>')

    # Garis Grid Horizontal
    for tick in [1000000, 2000000, 3000000, 4000000]:
        y = map_y(tick)
        label = f"{tick//1000000} Juta"
        svg.append(f'<line x1="{margin_l}" y1="{y}" x2="{width - margin_r}" y2="{y}" stroke="#e2e8f0" stroke-dasharray="4" stroke-width="1"/>')
        svg.append(f'<text x="{margin_l - 12}" y="{y + 4}" text-anchor="end" font-size="12" fill="#64748b">{label}</text>')

    svg.append(f'<text x="{margin_l - 12}" y="{map_y(0) + 4}" text-anchor="end" font-size="12" fill="#64748b">0</text>')

    # Sumbu X & Y
    svg.append(f'<line x1="{margin_l}" y1="{map_y(0)}" x2="{width - margin_r}" y2="{map_y(0)}" stroke="#334155" stroke-width="2"/>')
    svg.append(f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{map_y(0)}" stroke="#334155" stroke-width="2"/>')

    # Label Sumbu X
    for n in n_vals:
        x = map_x(n)
        svg.append(f'<line x1="{x}" y1="{map_y(0)}" x2="{x}" y2="{map_y(0) + 6}" stroke="#334155" stroke-width="2"/>')
        svg.append(f'<text x="{x}" y="{map_y(0) + 26}" text-anchor="middle" font-size="12" font-weight="bold" fill="#334155">{n:,}</text>')

    # Judul Sumbu
    svg.append(f'<text x="{width/2}" y="{height - 20}" text-anchor="middle" font-size="13" font-weight="bold" fill="#1e293b">Ukuran Data Masukan (n)</text>')
    svg.append(f'<text transform="rotate(-90)" x="{-height/2}" y="25" text-anchor="middle" font-size="13" font-weight="bold" fill="#1e293b">Jumlah Perbandingan</text>')

    # Garis Insertion Sort
    pts_ins = " ".join([f"{map_x(n)},{map_y(v)}" for n, v in zip(n_vals, ins_vals)])
    svg.append(f'<polyline points="{pts_ins}" fill="none" stroke="#e11d48" stroke-width="3.5" stroke-linecap="round"/>')

    # Titik Insertion Sort
    for n, v in zip(n_vals, ins_vals):
        cx, cy = map_x(n), map_y(v)
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="5.5" fill="#e11d48" stroke="#ffffff" stroke-width="2"/>')
        label_text = f"{v/1000000:.2f}M" if v >= 1000000 else f"{v/1000:.0f}K"
        svg.append(f'<text x="{cx - 10}" y="{cy - 12}" font-size="11" font-weight="bold" fill="#e11d48">{label_text}</text>')

    # Garis Merge Sort
    pts_mrg = " ".join([f"{map_x(n)},{map_y(v)}" for n, v in zip(n_vals, mrg_vals)])
    svg.append(f'<polyline points="{pts_mrg}" fill="none" stroke="#2563eb" stroke-width="3" stroke-linecap="round"/>')

    # Titik Merge Sort
    for n, v in zip(n_vals, mrg_vals):
        cx, cy = map_x(n), map_y(v)
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="5" fill="#2563eb" stroke="#ffffff" stroke-width="2"/>')

    # Anotasi Merge Sort di n = 4000
    x_mrg_last = map_x(4000)
    y_mrg_last = map_y(42760)
    svg.append(f'<text x="{x_mrg_last - 10}" y="{y_mrg_last - 12}" font-size="11" font-weight="bold" fill="#2563eb">42.760 (~42K)</text>')

    # Kotak Legenda
    leg_x = margin_l + 30
    leg_y = margin_t + 20
    svg.append(f'<rect x="{leg_x}" y="{leg_y}" width="260" height="75" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')

    # Item Legenda Insertion Sort
    svg.append(f'<line x1="{leg_x + 15}" y1="{leg_y + 25}" x2="{leg_x + 45}" y2="{leg_y + 25}" stroke="#e11d48" stroke-width="3"/>')
    svg.append(f'<circle cx="{leg_x + 30}" cy="{leg_y + 25}" r="4.5" fill="#e11d48"/>')
    svg.append(f'<text x="{leg_x + 55}" y="{leg_y + 29}" font-size="12" font-weight="bold" fill="#1e293b">Insertion Sort [O(n²)]</text>')

    # Item Legenda Merge Sort
    svg.append(f'<line x1="{leg_x + 15}" y1="{leg_y + 52}" x2="{leg_x + 45}" y2="{leg_y + 52}" stroke="#2563eb" stroke-width="3"/>')
    svg.append(f'<circle cx="{leg_x + 30}" cy="{leg_y + 52}" r="4.5" fill="#2563eb"/>')
    svg.append(f'<text x="{leg_x + 55}" y="{leg_y + 56}" font-size="12" font-weight="bold" fill="#1e293b">Merge Sort [O(n log n)]</text>')

    svg.append('</svg>')

    with open("grafik_sort.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print("Berhasil membuat file gambar: 'grafik_sort.svg'")

if __name__ == "__main__":
    buat_grafik_svg()