var options = {
	url: "static/countries.json",

	getValue: "name",

	list: {
		match: {
			enabled: true
		},
		maxNumberOfElements: 10,
		onSelectItemEvent: function() {
			var value = $("#provider-json").getSelectedItemData().code;

			$("#data-holder").val(value).trigger("change");
		},
	},
	highlightPhrase: true,

	theme: "bootstrap"
};

$("#provider-json").easyAutocomplete(options);