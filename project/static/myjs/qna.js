var myUserName = "{{ request.user.username }}";
var timeOptions = { hour12: true, hour: '2-digit', minute:'2-digit' };

// Sends a new request to update the to-do list
function getQnA() {
    $.ajax({
        url: "get-qna",
        dataType : "json",
        success: updateQnAPage,
        error: updateError
    });
}

function updateQnAPage(response) {
    if (typeof response === "object" && !Array.isArray(response)) {
        updateQuestions(response)
        updateAnswers(response)
    } else if (response.hasOwnProperty('error')) {
        displayError(response.error)
    } else {
        displayError(response)
    }
}

function updateError(xhr, status, error) {
    displayError('Status=' + xhr.status + ' (' + error + ')')
}

function displayError(message) {
    $("#error").html(message);
}

function updateQuestions(response) {
    // Removes the old todolist items
    // $("li").remove()


    // Adds each new post and comments to the displayed list of posts and comments (only if it's not already here)
    $(response['questions']).each(function() {
        let my_question = "id_question_" + this.id   //this.id = post.id because get_global_action()?how to determine id=?
        if (document.getElementById(my_post) == null) {
            // console.log(this)

            let date = new Date(this.creation_time)
            // post_date = date.toLocaleString().replace(/,/g, '')
            //.toLocaleFormat("m/d/yyyy h:m A")
            // .format("m/d/yyyy h:m A")
            question_date = date.toLocaleDateString() + " " + date.toLocaleTimeString('en', timeOptions)


            $("#qna-list").prepend(
                // no need {% for post in posts %}
                '<li id="id_question_' + this.id + '">' +    //this.id = question.id
                    '<span id="id_question_title_' + this.q_id + '">' + sanitize(this.q_title) + '</span>' +
                    '<span id="id_question_description_' + this.q_id + '">' + sanitize(this.q_desc + '</span>' + 
                    '<span id="id_question_date_time_' + this.q_id + '">' + question_date + '</span>' +
                    '<span id="id_follow_count_' + this.q_id + '">' + this.collect_count + '</span>' +
                    '<button type="button" class="collectButton">Add to Favourite</button>' +
                    '<span>New Answer:</span>' +
                    '<input id="id_answer_input_text_' + this.q_id + '" type="text" name="answer_text">' +
                    '<button id="id_answer_button_' + this.q_id + '" onClick="addAnswer(' + this.id + ', \'qna\')">Submit Answer</button>' +
                '</li>'
            )

        }
    });
}
// #1 comment list for each post
// # append each comment list to the related post
// name of list related to the post id
function updateAnswers(response) {
    // console.log(response)
    $(response['comments']).each(function() {
        let my_comment = "id_comment_" + this.comment_id   //this.id = post.id because get_global_action()?how to determine id=?
        if (document.getElementById(my_comment) == null) {

            let profileLink
            if (this.comment_by == myUserName) {
                profileLink = 'profile'
            } else {
                profileLink = 'profile_other'
            }

            let date = new Date(this.comment_date_time)
            comment_date = date.toLocaleDateString() + " " + date.toLocaleTimeString('en', timeOptions)

            $("#comment-list-"+this.post_id).append(
                '<li id="id_comment_' + this.comment_id + '">' +    //this.id = post.id
                '<a id="id_comment_profile_' + this.comment_id + '" href="/socialnetwork/' + profileLink +'/' + this.commenter_id + '">' +
                'Comment by ' + this.first_name + ' ' + this.last_name + ' </a>' +
                '<span id="id_comment_text_' + this.comment_id + '">' + sanitize(this.comment_text) + '</span>' +
                '<span id="id_comment_date_time_' + this.comment_id + '">' + comment_date + '</span>' +
                '</li>'
            )



            // getElementById
            // append the comment list to the corresponding post

        }
    })
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}

function addAnswer(id, page) {
    // console.log(id)
    let commentTextElement = $("#id_comment_input_text_"+id)
    let post_id = id
    let commentTextValue   = commentTextElement.val()

    // Clear input box and old error message (if any)
    commentTextElement.val('')
    displayError('');

    $.ajax({
        url: "/socialnetwork/add-comment",
        type: "POST",
        data: "comment_text="+commentTextValue+"&post_id="+id+"&page="+page+"&csrfmiddlewaretoken="+getCSRFToken(),
        dataType : "json",
        success: updateGlobalPage,
        error: updateError
    });
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown";
}


{% for question in questions %}
<li>
    <span id="id_question_title_{{ question.id }}">{{ question.question_title }}</span>
    <span id="id_question_description_{{ question.id }}">{{ question.question_description }}</span>
    <span id="id_question_date_time_{{ question.id }}">{{ question.question_creation_time|date:"n/j/Y g:i A" }}</span>
    <span id="id_follow_count_{{ question.id }}">{{ question.collect_count }}</span>
    <button type="button" class="collectButton">Add to Favourite</button>
    <form method="post">
        <span>New Answer:</span>
        <input type="text" id="id_answer_input_text_{{ question.id }}"> {% csrf_token %}
        <button id="id_answer_button_{{ question.id }}">Submit Answer</button>
    </form>

    <span>Recommended Answer:</span>
    <a href="{% url 'profile' %}" id="id_answer_profile_{{ answer.id }}">Answered by {{answer.answered_by_lawyer.user.first_name}} {{answer.answered_by_lawyer.user.last_name}}</a>
    <span id="id_answer_text_{{ answer.id }}">This is an answer</span>
    <span id="id_answer_date_time_{{ answer.id }}">{{ answer.answer_creation_time|date:"n/j/Y g:i A" }}M</span>
    <span id="id_like_count_{{ answer.id }}">{{ question.like_count }}</span>
    <button type="button" class="likeButton">Like</button>
    <button type="button" class="dislikeButton">Dislike</button>

    <button type="button" class="btn btn-info" data-toggle="collapse" data-target="#demo">Click to expand to see more answers</button>
    <div id="demo" class="collapse">
        More answers...
    </div>
</li>
{% endfor %}