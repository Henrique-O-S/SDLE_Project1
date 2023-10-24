    $(document).ready(function () {
        // When a form with the "deleteForm" class is submitted, prevent the default form submission and use Ajax instead
        $(".deleteForm").submit(function (e) {
            e.preventDefault(); // Prevent the default form submission
    
            // Get the form data for the specific form that was submitted
            var formData = {
                id: $(this).find(".id").val()
            };
    
            // Send a DELETE request to the server
            $.ajax({
                type: "DELETE",
                url: "/shopping_list?id=" + formData.id, // Update with the appropriate URL
                success: function (response) {
                    // Handle the response from the server
                    console.log("Server response:", response);
                    location.reload(); //reload page
                },
                error: function (error) {
                    console.error("Error:", error);
                    // Handle the error or show an error message
                }
            });
        });
    });
    
