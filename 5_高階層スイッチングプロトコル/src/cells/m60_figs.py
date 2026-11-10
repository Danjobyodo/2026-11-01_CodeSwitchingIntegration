# ==================================================================================================
# §6 図
# ==================================================================================================
fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
for N in sorted(RES.N.unique()):
    sub = RES[RES.N == N]
    ax[0].loglog(sub.L, sub.qubits, 'o-', label=f'N={N} ({N - 1}D)')
    ax[1].semilogy(sub.L, sub['X誤りの広がり_最大'], 's-', label=f'N={N}')
ax[0].set_xlabel('L'); ax[0].set_ylabel('physical qubits (data)'); ax[0].set_title('qubits vs. lattice size'); ax[0].legend(prop={'size': 8})
ax[1].set_xlabel('L'); ax[1].set_ylabel('max. qubits sharing a gate of W with one qubit'); ax[1].set_title('spread of one X error through U'); ax[1].legend()
if 'L' in BE.columns and BE.L.notna().any():
    for delta in sorted(BE.delta.unique()):
        sub = BE[(BE.delta == delta) & BE.L.notna()]
        if len(sub) == 0:
            continue
        ax[2].semilogy(sub.L, sub['許されるステップ数'], 'o-', label=f'allowed, delta={delta:g}')
    Ls = np.array(sorted(BE.L.dropna().unique()))
    ax[2].semilogy(Ls, 62 * Ls + 21, 'k--', label='2D T switching (study 3): 62 L + 21')
ax[2].set_xlabel('L (3D code)'); ax[2].set_ylabel('time steps'); ax[2].set_title('break-even time budget for sqrt(T), N=4'); ax[2].legend(prop={'size': 8})
for a in ax:
    a.grid(True, which='both', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'fig_study5.png'), dpi=150)
plt.show()
