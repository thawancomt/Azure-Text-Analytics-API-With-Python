const formUser = $('#input-user')
const sendButton = $('#send-button')
const userInpt = $('#user-entry')


userInpt.on( 
    {
        "input" : () => {
            if (userInpt.val()) {
                sendButton.removeClass('hidden')
                userInpt.addClass('animate-pulse')
            } else {
                userInpt.removeClass('w-3/4')
                sendButton.addClass('hidden')
            }
        }
    }
);

var response = {};

function setResponse(data) {
    response = data;

    for (sentence of response.sentiment.sentences) {
        $("#sentencesBody").append(
            `<tr class="text-left text-gray-700">
                <td>${sentence.text}</td>
                <td>${sentence.offset}</td>
                <td>${sentence.sentiment_name}</td>
                <td>${sentence.confidence}</td>
            </tr>`
        );
    }
    for (entity of response.entities.entities) {
        $("#entitiesBody").append(
            `<tr class="text-left text-gray-700">
                <td>${entity.entity_name}</td>
                <td>${entity.category}</td>
                <td>${entity.sub_category}</td>
                <td>${entity.offset}</td>
                <td>${entity.confidence}</td>
            </tr>`
        );
    };
}

sendButton.on('click', () => {
    $.post('/get', { text: userInpt.val() }, setResponse, 'json');
});
