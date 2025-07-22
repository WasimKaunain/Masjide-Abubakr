document.getElementById("cashDonationForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData);

  const response = await fetch('/submit-cash', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  console.log("Form data being sent:", data);
  console.log("Response status:", response.status);


  const result = await response.json();
  if (result.success) {
    window.location.href = '/';
    alert("Cash donation recorded!");
  } else {
    alert("Error submitting donation.");
  }
});
