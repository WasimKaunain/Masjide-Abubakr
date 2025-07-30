
function goToPayment() 
{
    const payeeName = document.getElementById("payee-name-input").value.trim();
    const amount = parseFloat(document.getElementById("final-amount-display").innerText);

    if (!payeeName) {
      alert("Please enter the payee name.");
      return;
    }

    fetch("/create_order", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ amount: amount } ) } )
    .then(res => res.json())
    .then(data => { 
                      if (data.status !== "success") 
                          {
                              alert("Failed to create payment order.");
                              return;
                          }
                        
                      const options = 
                      {
                        key: data.key,  // Razorpay public key from server response
                        amount: data.amount, // Already in paise from server
                        currency: data.currency,
                        name: "Tarique Digital Solutions",
                        description: "Payment for services",
                        order_id: data.order_id,
                        
                        handler: function (response) 
                        {
                          fetch ("/verify_payment", { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(
                                                                                                                                          {
                                                                                                                                          razorpay_payment_id: response.razorpay_payment_id,
                                                                                                                                          razorpay_order_id: response.razorpay_order_id,
                                                                                                                                          razorpay_signature: response.razorpay_signature
                                                                                                                                          }
                                                                                                                                         )
                                                    }
                                ).then(res => res.json())
                                 .then(verifyData => {
                                                  if (verifyData.status === "success") 
                                                      {
                                                          alert("Payment verified and successful!");
                                                          fetch("/payment-success", {method : "POST", headers: {"Content-Type" : "application/json"}, body : JSON.stringify(
                                                                                                                                                                            {
                                                                                                                                                                                name:payeeName,
                                                                                                                                                                                amount:data.amount
                                                                                                                                                                            }
                                                                                                                                                                            )
                                                                                    }).then(res => res.json()).then(successLog =>   {
                                                                                                                                        if (successLog.status === "success")
                                                                                                                                            {
                                                                                                                                                console.log("Payment details stored in sheet.")
                                                                                                                                            }
                                                                                                                                        else
                                                                                                                                           {
                                                                                                                                                console.warn("Failed to log payment sheet.")
                                                                                                                                           }
                                                                                                                                    }
                                                                                                                    ).catch(err =>  { console.error("Error logging payment success",err); })
                                                      } 
                                                  else 
                                                      {
                                                          alert("Payment failed verification!");                                  
                                                      }
                                              }
                                ).catch(err =>   {
                                          console.error(err);
                                          alert("An error occurred during verification.");
                                          });
                        },
                      
                        prefill   : { name: payeeName},
                      
                        notes     : { payee_name: payeeName },
                      
                        theme     : { color: "#28a745" },
                      
                        modal     : { ondismiss: function () { alert("Payment popup closed."); } }
                      };
                    
                      const rzp = new Razorpay(options);
                      rzp.open();
                  }).catch(err => {
                                      console.error(err);
                                      alert("Something went wrong while creating the order.");
                                  });
}   
