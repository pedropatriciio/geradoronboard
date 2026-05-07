// ================================
// CONFIGURAÇÃO
// ================================
const BACKEND_URL = "https://geradoronboard.onrender.com";

// ================================
// ELEMENTOS DO DOM
// ================================
const form = document.getElementById("pptForm");
const comercialSelect = document.getElementById("comercial");
const csSelect = document.getElementById("cs");
const statusMessage = document.getElementById("statusMessage");

// ================================
// CARREGAR COLABORADORES (SUPABASE)
// ================================
async function carregarColaboradores() {
  try {
    const response = await fetch(`${BACKEND_URL}/colaboradores`);

    if (!response.ok) {
      throw new Error("Falha ao buscar colaboradores");
    }

    const colaboradores = await response.json();

    // Limpa selects
    comercialSelect.innerHTML = '<option value="">Selecione</option>';
    csSelect.innerHTML = '<option value="">Selecione</option>';

    colaboradores.forEach((pessoa) => {
      const option = document.createElement("option");
      option.value = pessoa.nome;
      option.textContent = pessoa.nome;

      if (pessoa.papel === "Comercial") {
        comercialSelect.appendChild(option);
      }

      if (pessoa.papel === "CS") {
        csSelect.appendChild(option);
      }
    });

    statusMessage.textContent = "";

  } catch (error) {
    console.error("Erro ao carregar responsáveis:", error);
    statusMessage.textContent = "Erro ao carregar responsáveis.";
  }
}

// ================================
// SUBMIT DO FORMULÁRIO
// ================================
form.addEventListener("submit", async (event) => {
  event.preventDefault();

  statusMessage.textContent = "Gerando apresentação...";

  const formData = new FormData(form);

  try {
    const response = await fetch(`${BACKEND_URL}/generate`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Erro ao gerar apresentação");
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = "Onboarding_CS.pptx";
    document.body.appendChild(a);
    a.click();
    a.remove();

    statusMessage.textContent = "Apresentação gerada com sucesso!";

  } catch (error) {
    console.error(error);
    statusMessage.textContent = "Erro ao gerar apresentação.";
  }
});

// ================================
// INICIALIZAÇÃO
// ================================
document.addEventListener("DOMContentLoaded", carregarColaboradores);