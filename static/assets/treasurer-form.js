document.getElementById("cashDonationForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData);

  const response = await fetch('/pay-salary', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  const result = await response.json();
  if (result.success) {
    window.location.href = '/';
    alert("Salary Payment recorded!");
  } else {
    alert("Error submitting Salary form.");
  }
});
