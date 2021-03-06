function get_notifications(){ 
	$.get($('#notification-count').data('ajaxUrl'),
	{
		'mode' : 'count'
	},
	function(data){
		$('#notification-count').html(data);
	},
	'html'
	);

	$.get($('#notification-body').data('ajaxUrl'),
	{
		'mode' : 'body'
	},
	function(data){
		$('#notification-body').html(data);
	},
	'html'
	);
}

function search_contacts(page=1){
	$.get($('#search-contacts').data('ajaxUrl'),
	{
		'search_text' : $('#search-contacts').val(),
		'mode' : 'contacts',
		'page' : '' + page,
	},
	function(data){
		$('#search-results-contacts').html(data);
	},
	'html'
	);
}

$(function(){
	$.ajaxSetup({
	    error: function(xhr){
	    	if (xhr.status >=400){
	        	alert('Error!\n Request Status: ' + xhr.status + ' Status Text: ' + xhr.statusText);
	    	}
	    }
	});

	if( $('body').data('userStatus') == 'True'){
		get_notifications();

		setInterval(function(){
			get_notifications();
		}, 5000);
		
		$('body').on('click', '#notification-icon', function(){
			document.getElementById('notification-body').classList.toggle('show');
			$.get($(this).data('ajaxUrl'),
			{
				'last' : $('#notification-count-value').data('last'),
			},
			function(data){
				if(data.response == 'success'){
					get_notifications();
				}
			}
			);
		});
	}

	$('#search-users').keyup(function(){
		$.get($(this).data('ajaxUrl'),
			{
				'search_text' : $(this).val(),
			},
			function(data){
				$('#search-results-users').show();
				$('#search-results-users').html(data);
			},
			'html'
		);
	});

	$('body').on('click', '#view-all-button', function () {
		window.location = $('#view-all-button').data('ajaxUrl') + 'keyword='+ $('#search-users').val();
	});

	$('body').on('click', '#remove-picture', function (){
		$.get($(this).data('ajaxUrl'),
		{
			'mode' : $(this).attr('id')
		},
		function(){
			location.reload();
		}
		);
	});

	if( window.location.pathname == $('#contacts-url').attr('href') ){	
		search_contacts();
		$('#search-contacts').keyup( search_contacts );
	}

	$('.ajax-contact-button').click(function(){
		console.log('test')
		$.post($(this).data('ajaxUrl'),
		{
			'user_id' : $(this).data('userId'),
			'choice' : $(this).attr('id'),
			'csrfmiddlewaretoken' : $('input[name=csrfmiddlewaretoken]').val()
		},
		function(){
			location.reload();
  		},
  		'json'
  		);
		
  	});

	$('.block-button').click(function(){
		$.get($(this).data('ajaxUrl'),
		function(){
			location.reload();
  		},
  		'json'
  		);
  	});

  	$('body').on('click', '.paginator', function(){
		search_contacts($(this).data('page'));
  	});
});
