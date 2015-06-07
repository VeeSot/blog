var app = app || {};

app.PostView = Backbone.View.extend({
    tagName: 'li class="preview"',
    postPreview: _.template($('#post-preview').html()),

    render: function () {
        this.$el.html(this.postPreview(this.model.toJSON()));
        return this;
    }
});


app.AppView = Backbone.View.extend({
    initialize: function () {
        this.listenTo(app.Posts, 'add', this.addOne);
        this.listenTo(app.Posts, 'reset', this.addAll);
        app.Posts.fetch({data: {fields: 'title,slug,created_at,img'}});
    },
    addOne: function (post) {
        var view = new app.PostView({model: post});
        $('#posts').append(view.render().el);
    },
    addAll: function () {
        app.Post.each(this.addOne, this);
    }
});
