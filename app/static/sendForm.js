const formUser = $('#input-user')
const sendButton = $('#send-button')
const userInpt = $('#user-entry')
const historicButton = $('#historic-button')


userInpt.on( 
    {
        "input" : () => {
           sendButton.toggleClass('hidden');
        }
    }
);

var response = null;

function setResponse(data) {
    console.log(data);
    if (response) {
        $("#sentencesBody").empty();
        $("#entitiesBody").empty();
        $("#linkedEntitiesBody").empty();
        $("#tagsBody").empty();
    }
    response = data;

    for (sentence of response.sentiment.sentences) {
        $("#sentencesBody").append(
            `<tr class="text-left text-gray-700">
                <td>${sentence.text}</td>
                <td>${sentence.offset}</td>
                <td>${sentence.sentiment_name }</td>
                <td>${sentence.confidence}</td>
            </tr>`
        );
    }
    for (entity of response.entities.entities) {
        $("#entitiesBody").append(
            `<tr class="text-left text-gray-700">
                <td>${entity.entity_name}</td>
                <td>${entity.category}</td>
                <td>${entity.subcategory}</td>
                <td>${entity.offset}</td>
                <td>${entity.confidence}</td>
            </tr>`
        );
    }
    for (linkedEntity of response.linked_entities.linked_entities) {
        $("#linkedEntitiesBody").append(
            `<tr class="text-left text-gray-700">
                <td>${linkedEntity.name}</td>
                <td>${linkedEntity.url}</td>
                <td>${linkedEntity.data_source}</td>
                <td>${linkedEntity.matches.text} || ${linkedEntity.matches.confidence_score}</td>
            </tr>`
        );
    }
    for (tag of response.key_phrases.tags) {
        $("#tagsBody").append(`
            <h1 class="tags">${tag.name}</h1>
        `);
    }
}

sendButton.on('click', () => {
    $.post('/get', { text: userInpt.val() }, setResponse, 'json');
});

historicButton.on('click', () => {
    showHistoric();
});


function showHistoric() {
    $.get('/get_historic', (response) => {
        $("#historicList").empty();

        response.inputs.forEach((input, index) => {
            // Atribui um identificador único usando o índice
            const listItem = $(`<li class="text-left p-2 text-white" data-index="${index}">${input.text}</li>`);
            
            listItem.on('click', (event) => {
                const clickedText = $(event.target).text();
                console.log(clickedText);
                
                $.post('/get', { text: clickedText.toString() }, setResponse, 'json');
                
            });

            $("#historicList").append(listItem);
        });

        $("#historic").toggleClass('hidden');
    }, 'json');
}