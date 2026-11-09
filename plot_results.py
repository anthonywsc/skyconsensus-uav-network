from pathlib import Path
import matplotlib.pyplot as plt

Path('results').mkdir(exist_ok=True)
rounds = list(range(16))
disagreement = [20, 12.0, 8.2, 5.7, 4.0, 2.9, 2.1, 1.5, 1.05, .74, .52, .37, .26, .18, .13, .09]
fig, ax = plt.subplots(figsize=(7.2, 3.8))
ax.plot(rounds, disagreement, marker='o', ms=3.5, lw=2, color='#2166ac')
ax.set(xlabel='Consensus round', ylabel='Max-min estimate', title='Distributed consensus convergence')
ax.grid(alpha=.25); fig.tight_layout(); fig.savefig('results/consensus_convergence.png', dpi=160); plt.close(fig)
