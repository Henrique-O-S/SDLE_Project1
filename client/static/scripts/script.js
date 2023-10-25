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

    $.ajax({
        type: "PUT",
        url: "shopping_list",
        data: data,
        dataType: 'text',
        success: function (data) {

            let final = JSON.parse(data);

            // Update the displayed quantity if the update was successful
            const quantityDisplayElement = document.getElementById(`quantity_${item_name}`);
            quantityDisplayElement.textContent = final.new_quantity;
        },
        error: function (data) {
            // Handle any errors or display error messages to the user
            console.error(data.error);
        }
    });
    return false;
}








