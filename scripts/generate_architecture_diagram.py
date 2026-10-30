"""Generate a clean, publication-quality architecture diagram for ForensiGuard."""

import matplotlib.pyplot as plt

def draw_architecture():
    fig, ax = plt.subplots(figsize=(10.5, 4.2), dpi=300)
    ax.axis("off")
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 4.2)

    # Style parameters
    box_gray = dict(boxstyle="round,pad=0.4", facecolor="#F1F3F4", edgecolor="#5F6368", lw=1.5)
    box_blue = dict(boxstyle="round,pad=0.35", facecolor="#E8F0FE", edgecolor="#1A73E8", lw=1.5)
    box_green = dict(boxstyle="round,pad=0.35", facecolor="#E6F4EA", edgecolor="#137333", lw=1.5)
    box_amber = dict(boxstyle="round,pad=0.35", facecolor="#FEF7E0", edgecolor="#B06000", lw=1.5)
    box_purple = dict(boxstyle="round,pad=0.4", facecolor="#F3E8FD", edgecolor="#7627BB", lw=1.5)
    box_red = dict(boxstyle="round,pad=0.4", facecolor="#FCE8E6", edgecolor="#C5221F", lw=1.5)

    arrow_props = dict(arrowstyle="-|>", lw=1.5, color="#202124", mutation_scale=12)

    # Tier 1: Input Evidence
    ax.text(0.9, 2.1, "Input Digital\nEvidence Artifact\n\n$x_i = (M_i, B_i, E_i)$\nFilesystem Files", 
            ha="center", va="center", bbox=box_gray, fontsize=8.5, fontweight="bold")

    # Tier 2: Feature Extractors & Base Models
    # Modality 1: Metadata
    ax.text(3.7, 3.4, "Modality 1: Filesystem Metadata\n"
                      r"$\bullet$ Timestamp Deltas ($\Delta_{m,c}, \Delta_{a,m}$)" "\n"
                      r"$\bullet$ Directory Context $z$-Scores ($z_m$)" "\n"
                      r"$\bullet$ Clean-Trained Isolation Forest ($S_{\mathrm{anom}}$)" "\n"
                      r"$\bullet$ Metadata XGBoost Classifier $\to P_{\mathrm{meta}}$",
            ha="center", va="center", bbox=box_blue, fontsize=8)

    # Modality 2: Image Residual CNN
    ax.text(3.7, 2.1, "Modality 2: Spatial Noise Residuals\n"
                       r"$\bullet$ Ker-Vannier $5\times 5$ High-Pass Filter ($K_{\mathrm{KV}}$)" "\n"
                       r"$\bullet$ Residual Normalization \& Clipping" "\n"
                       r"$\bullet$ SRNet-Lite Residual CNN" "\n"
                       r"$\bullet$ Spatial Steganalysis Model $\to P_{\mathrm{image}}$",
            ha="center", va="center", bbox=box_green, fontsize=8)

    # Modality 3: Structural Integrity
    ax.text(3.7, 0.8, "Modality 3: File Signature & Bytes\n"
                      r"$\bullet$ Magic-Byte vs. Extension Verification" "\n"
                      r"$\bullet$ Shannon Byte Entropy $H(B)$" "\n"
                      r"$\bullet$ LSB Pairs Chi-Square Independence ($p_{\mathrm{lsb}}$)" "\n"
                      r"$\bullet$ Signature Inconsistency Flag $\to S_{\mathrm{sig}}$",
            ha="center", va="center", bbox=box_amber, fontsize=8)

    # Tier 3: Late Fusion Meta-Learner
    ax.text(6.8, 2.1, "Grouped Out-of-Fold\nLate Fusion Meta-Learner\n\n"
                       r"$v_{\mathrm{fuse}} \in \mathbb{R}^7 \text{ Meta-Vector}$" "\n"
                       r"$\bullet$ Stacked Logistic Meta-Model" "\n"
                       r"$\bullet$ Validation Threshold $\tau^* = 0.500$",
            ha="center", va="center", bbox=box_purple, fontsize=8.5, fontweight="bold")

    # Tier 4: Output & Triage Decision
    ax.text(9.4, 2.1, "Defensible Forensic\nTriage Output\n\n"
                       r"$\bullet$ Probability $P(\mathrm{manip})$" "\n"
                       r"$\bullet$ 5-Class Technique Attribution" "\n"
                       r"$\bullet$ Local TreeSHAP Feature Insights" "\n"
                       r"$\bullet$ Court-Ready Forensic Report",
            ha="center", va="center", bbox=box_red, fontsize=8.5, fontweight="bold")

    # Draw Arrows with clear coordinates
    ax.annotate("", xy=(2.0, 3.4), xytext=(1.6, 2.4), arrowprops=arrow_props)
    ax.annotate("", xy=(2.0, 2.1), xytext=(1.6, 2.1), arrowprops=arrow_props)
    ax.annotate("", xy=(2.0, 0.8), xytext=(1.6, 1.8), arrowprops=arrow_props)

    ax.annotate("", xy=(5.4, 2.4), xytext=(5.1, 3.2), arrowprops=arrow_props)
    ax.annotate("", xy=(5.4, 2.1), xytext=(5.1, 2.1), arrowprops=arrow_props)
    ax.annotate("", xy=(5.4, 1.8), xytext=(5.1, 1.0), arrowprops=arrow_props)

    ax.annotate("", xy=(8.3, 2.1), xytext=(8.0, 2.1), arrowprops=arrow_props)

    plt.tight_layout()
    output_path = "paper/figures/fig0_architecture.png"
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"Architecture diagram successfully updated at {output_path}")

if __name__ == "__main__":
    draw_architecture()
