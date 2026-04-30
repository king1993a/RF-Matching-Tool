import numpy as np
import skrf as rf
import matplotlib.pyplot as plt

def s11_db(Zin, ZS):
    gamma = (Zin - ZS.conjugate()) / (Zin + ZS)
    return 20 * np.log10(np.abs(gamma) + 1e-15)

def z_to_gamma(Z, Z0=50):
    return (Z - Z0) / (Z + Z0)

def get_component_str(val, is_b, freq):
    """根據 B (電納) 或 X (電抗) 計算元件值"""
    w = 2 * np.pi * freq
    if is_b: # 並聯元件 (Shunt)
        if val > 0: return f"{val/w*1e12:.2f} pF (C)"
        else: return f"{-1/(w*val)*1e9:.2f} nH (L)"
    else: # 串聯元件 (Series)
        if val > 0: return f"{val/w*1e9:.2f} nH (L)"
        else: return f"{-1/(w*val)*1e12:.2f} pF (C)"

def get_smooth_path(z_start, z_end, is_shunt):
    pts = 50
    if not is_shunt:
        r = np.real(z_start)
        xi = np.linspace(np.imag(z_start), np.imag(z_end), pts)
        return r + 1j*xi
    else:
        y_start, y_end = 1/z_start, 1/z_end
        g = np.real(y_start)
        bi = np.linspace(np.imag(y_start), np.imag(y_end), pts)
        return 1 / (g + 1j*bi)

def solve_and_plot_matching(ZS, ZL, freq, Z0=50):
    RL, XL = np.real(ZL), np.imag(ZL)
    RS, XS = np.real(ZS), np.imag(ZS)
    R_target, X_target = RS, -XS 
    
    results = []
    # --- 策略 1: Series-Shunt ---
    if RL <= RS + 1e-6:
        diff = RL * RS - RL**2
        delta = np.sqrt(max(0, diff))
        for sign in [1, -1]:
            X_ser = sign * delta - XL
            Z_mid = ZL + 1j*X_ser
            Y_target, Y_mid = 1/(RS + 1j*X_target), 1/Z_mid
            B_shunt = np.imag(Y_target - Y_mid)
            results.append({'type': 'Series-Shunt', 'B': B_shunt, 'X': X_ser, 'Z_mid': Z_mid})

    # --- 策略 2: Shunt-Series ---
    GL, G_target = np.real(1/ZL), 1/RS
    if GL <= G_target + 1e-9:
        BL = np.imag(1/ZL)
        delta = np.sqrt(max(0, GL * G_target - GL**2))
        for sign in [1, -1]:
            B_shunt = sign * delta - BL
            Z_mid = 1/(1/ZL + 1j*B_shunt)
            X_ser = X_target - np.imag(Z_mid)
            results.append({'type': 'Shunt-Series', 'B': B_shunt, 'X': X_ser, 'Z_mid': Z_mid})

    fig, ax = plt.subplots(figsize=(10, 10))
    dummy_f = rf.Frequency(freq/1e9, freq/1e9, 1, 'ghz')
    dummy_ntw = rf.Network(f=dummy_f.f, s=[[[0]]], z0=Z0)
    dummy_ntw.plot_s_smith(ax=ax, draw_labels=True)
    ax.set_title(f'Matching @ {freq/1e9:.2f}GHz: {ZL} -> {ZS.conjugate()}')

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    valid_count = 0
    print(f"{'方案':<5} | {'拓樸':<15} | {'Step 1 (Load)':<18} | {'Step 2 (Source)':<18} | {'S11':<8}")
    print("-" * 75)

    for i, sol in enumerate(results):
        Z_mid = sol['Z_mid']
        if sol['type'] == 'Series-Shunt':
            comp1 = get_component_str(sol['X'], False, freq)
            comp2 = get_component_str(sol['B'], True, freq)
            path1, path2 = get_smooth_path(ZL, Z_mid, False), get_smooth_path(Z_mid, 1/(1/Z_mid + 1j*sol['B']), True)
            Z_final = 1 / (1/Z_mid + 1j*sol['B'])
        else:
            comp1 = get_component_str(sol['B'], True, freq)
            comp2 = get_component_str(sol['X'], False, freq)
            path1, path2 = get_smooth_path(ZL, Z_mid, True), get_smooth_path(Z_mid, Z_mid + 1j*sol['X'], False)
            Z_final = Z_mid + 1j*sol['X']

        s11 = s11_db(Z_final, ZS)
        if s11 < -30:
            valid_count += 1
            label_str = f"Opt {valid_count}: {comp1} + {comp2}"
            rf.Network(f=dummy_f.f, z=path1, z0=Z0).plot_s_smith(ax=ax, color=colors[i%4], lw=2, label=label_str)
            rf.Network(f=dummy_f.f, z=path2, z0=Z0).plot_s_smith(ax=ax, color=colors[i%4], lw=2, linestyle='--')
            print(f"{valid_count:<6} | {sol['type']:<15} | {comp1:<18} | {comp2:<18} | {s11:>5.1f}dB")

    # 標註起點終點
    gl, gt = z_to_gamma(ZL), z_to_gamma(ZS.conjugate())
    ax.plot(gl.real, gl.imag, 'ro', ms=8); ax.text(gl.real, gl.imag+0.05, 'ZL', color='red', ha='center', weight='bold')
    ax.plot(gt.real, gt.imag, 'gs', ms=8); ax.text(gt.real, gt.imag-0.08, 'Target(ZS*)', color='green', ha='center', weight='bold')
    
    plt.legend(loc='upper right', fontsize='small')
    plt.show()

if __name__ == "__main__":
    solve_and_plot_matching(ZS=10+5j, ZL=200-8j, freq=2.4e9)