function updateQuantity(item_name, shopping_list_id) {

    $.ajaxSetup({
        headers: {
            'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content')
        }
    });
    
    const quantity_element = document.getElementById(`quantity_${item_name}`);
    const new_quantity = quantity_element.value;

    // Construct the data to send to the server
    const data = {
        item_name: item_name,
        new_quantity: new_quantity,
        shopping_list_id: shopping_list_id
    };

    console.log(data);

    $.ajax({
        type: "PUT",
        url: "shopping_list",
        contentType: "application/json",
        data: JSON.stringify(data),
        success: function (response) {

            // Update the displayed quantity if the update was successful
            const quantityDisplayElement = document.getElementById(`quantity_${item_name}`);
            quantityDisplayElement.textContent = new_quantity;
        },
        error: function (error) {
            // Handle any errors or display error messages to the user
            console.error("Error:", error);
        }
    });
    return false;
}








