var app = app || {};

app.TagView = Backbone.View.extend({
    tagName: 'li class="tag"',
    postPreview: _.template($('#tag').html()),

    render: function () {
        this.$el.html(this.postPreview(this.model.toJSON()));
        return this;
    }
});


app.TagListView = Backbone.View.extend({
    initialize: function () {
        this.listenTo(app.Tags, 'add', this.addOne);
        this.listenTo(app.Tags, 'reset', this.addAll);
        app.Tags.fetch({data: {count: 8,random_order:true}});
    },
    addOne: function (post) {
        var view = new app.TagView({model: post});
        $('#tags').append(view.render().el);
    },
    addAll: function () {
        app.Tag.each(this.addOne, this);
    }
});
