
let upiId = "";

fetch("/config")
  .then(res => res.json())
  .then(data => {
    upiId = data.upiId;  // ✅ coming from env variable
  });

function goToPayment() {
  if (selectedAmount > 0) {
    const name = encodeURIComponent("Mosque Donation");
    const url = `upi://pay?pa=${upiId}&pn=${name}&am=${selectedAmount}&cu=INR`;

    // Open in same tab (works on mobile)
    window.location.href = url;

  } else {
    alert("Please select a donation amount first!");
  }

  
}
