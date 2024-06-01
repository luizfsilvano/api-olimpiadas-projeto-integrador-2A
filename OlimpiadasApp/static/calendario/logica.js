// URL do servidor
var url = 'https://olimpiadasiesb-7780607c931d.herokuapp.com/esportes/partidas';
var token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6Imx1aXpmc2lsdmFubyIsInVzZXJfdHlwZSI6ImFkbWluIn0.0DMWIt-V4l7NfGHhd2q518Nv1TxTNbAPKEkTHeubFjc';

var headers = new Headers();
headers.append('Authorization', 'Bearer ' + token);

fetch(url, { headers: headers })
    .then(response => response.json())
    .then(eventos => {
        // Transforma os eventos para o formato esperado pelo evoCalendar
        var calendarEvents = eventos.map(function(evento, index) {
            var data = new Date(evento.data);
            var formattedDate = data.getFullYear() + '-' + (data.getMonth() + 1).toString().padStart(2, '0') + '-' + data.getDate().toString().padStart(2, '0') + ' ' + index + ':00:00';
            var participantes = evento.participantes.join(', ');
            console.log(formattedDate)
            return {
                id: evento._id,
                name: evento.esporte_nome,
                date: formattedDate,
                description: participantes,
                type: 'event'
            };
        });

        // Inicializa o evoCalendar com os eventos
        $('#calendar').evoCalendar({
            calendarEvents: calendarEvents,
            language: 'pt'
        });
    })
    .catch(error => console.error('Error:', error));