/*
Copyright (c) 2009 GOcipher.

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/

/*** Maps Section ***/
	var map = null;
	var mgr = null;

	/*** Initializes the googlemap ***/
	function setupMap() 
	{
		if (GBrowserIsCompatible()) 
		{
			map = new GMap2(document.getElementById("map"));
			map.addControl(new GLargeMapControl());
			map.setCenter(new GLatLng(35, 5), 2);
			window.setTimeout(setupMarkers, 0);
			GEvent.addListener(map,'click',function(overlay,latlng){
				if (latlng)
				{
					map.setZoom(map.getZoom()+2); 
					map.setCenter(latlng);
				}
			});
		}
	}

	/*** Paints the markers, the first time paints the cities markers, second one paints the contacts markers  ***/
	function setupMarkers() 
	{
		getMarkers(1);  
		getMarkers(2);
	}

	/*** Gets the latitude and longitude of each city and contact 
			int type : if type=1 use the cities object
					   else use the contacts object
	***/
	function getMarkers(type) 
	{
		var batch = [];
		
		if (type == 1)
			n = cities.length;
		else
			n = contacts.length;
		for (var i = 0; i < n; ++i) 
		{
			var point = getPoint(i,type);
			var marker = new GMarker(point, { icon: getIcon(type) });
			GEvent.addListener(marker, 'click',newfunc(point,marker));
			batch.push(marker);
			mgr = new MarkerManager(map);
			if (type == 1)
				mgr.addMarkers(batch, 1, 4);
			else
				mgr.addMarkers(batch, 5);
			mgr.refresh();
			batch.pop(); 	
		}
	}

	/*** Returns the corresponding icon depending if is a city or a contact 
		int type : if 1 use the city icon else use the contact icon
	***/
	function getIcon(type) 
	{	
		var icon = new GIcon(G_DEFAULT_ICON);
		if (type == 1)
			icon.image = media_url+"images/blue-dot.png";
		else
			icon.image = media_url+"images/yellow-dot.png";
		
		icon.shadow = media_url+"images/shadow50.png";
		icon.iconSize = new GSize(32, 34);
		icon.shadowSize = new GSize(38, 34);
		icon.iconAnchor = new GPoint(15, 34);
		return icon;	
	}

	/*** Returns a GLatLng object (point in the map)
		int i : the index of the object to search
		int type: the object where to search (1 = cities else contacts)
	***/
	function getPoint(i,type) 
	{
		var lat = 0;
		var lng = 0;
		if (type == 1)
		{
			lat = cities[i]['latitude'];
			lng = cities[i]['longitude'];
		}
		else
		{
			lat = contacts[i]['latitude'];
			lng = contacts[i]['longitude'];
		}
		return new GLatLng(lat,lng);
	}

	/*** Returns the html infoWindow of specific the marker, the function receives the coordinates and then search for the name and/or organization
		 in both objects (cities and contacts)
		 GLatLng latlng = the latitude and longitude object of the specific marker
	***/
	function getPointName(latlng)
	{
		var str = latlng.toString();
		str = str.replace("(",'');
		str = str.replace(")",'');
		var arr = str.split(',');
		var html = "";
		for (city in cities)
		{
			if (cities[city].latitude == arr[0] && cities[city].longitude == arr[1])
			{
				html += "<br /><span class='infoMap1'>City:&nbsp;</span>"+
						"<span class='infoMap2'>"+cities[city].name+"</span>"+
						"<br />";
			}
		}
		for (contact in contacts)
		{
			if (contacts[contact].latitude == arr[0] && contacts[contact].longitude == arr[1])
			{
				html += "<span class='infoMap1'>contact:&nbsp;</span>"+
						"<span class='infoMap2'>"+contacts[contact].name+"</span> <br /><br />"+
						"<span class='infoMap1'>Organization:&nbsp;</span>"+
						"<span class='infoMap2'>"+contacts[contact].organization+"</span>";
			}
		}
		
		return html;
	}

	/*** This is a procedure its called from the GEvent.addListener of each marker
		GLatLng arg : the latitude and longitude object of the specific marker
		arg2 : the marker where the infoWindow will appear when clicked
	***/
	newfunc = function (arg, arg2){	return function(evt){arg2.openInfoWindowHtml(getPointName(arg));};}

/*** end maps section ***/

/*** Contacts Import ***/
	// Freshbooks import
	$(function() {
		$("#freshbooks-import").dialog({
			bgiframe: true,
			width: 600,
			modal: true,
			autoOpen: false,
			closeOnEscape: false,
			resizable: false,
			buttons: {
				"Import": function() {
					var CONTACTS_PER_REQUEST = 10;
					var setupPage = 1;
					var contactsToImport = [];
					var contactsAlreadyImported = [];
					var progressPerRequest = 0;
					
					// Utility Functions
					var clearForm = function() {
						setupPage = 1;
						contactsToImport = [];
						contactsAlreadyImported = [];
						progressPerRequest = 0;
						$('#freshbooks-import-status').text('');
						$("#freshbooks-import-progressbar").progressbar('option', 'value', 0);
						$("#freshbooks-import-progressbar").css('visibility', 'hidden');
					}
					
					var disableForm = function() {
						$('.ui-dialog-titlebar-close').hide();
						$('.ui-dialog-buttonpane button').hide();
					}
					
					var enableForm = function() {
						$('.ui-dialog-titlebar-close').show();
						$('.ui-dialog-buttonpane button').show();
					}
					
					// Clear the form at the beginnig of the import process
					clearForm();
					
					// Check that the required fields are present
					var username = $('#username').val();
					var token = $('#token').val();
					if(username === '') {
						$('#username').effect('pulsate', { times: 2 }, 1000);
						$('#freshbooks-import-status').text('Please enter your Freshbooks Username');
						return false;
					}
					if(token === '') {
						$('#token').effect('pulsate', { times: 2 }, 1000);
						$('#freshbooks-import-status').text('Please enter your Freshbooks Token');
						return false;
					}
					
					// Everything ok, now disable buttons to prevent unfinished imports
					disableForm();
					$('#freshbooks-import-status').text('Setting up the Import Process');
					
					var importContacts = function() {
						var _contacts = [];
						for (var i=0; i < CONTACTS_PER_REQUEST && contactsToImport.length; i++) {
							_contacts[_contacts.length] = contactsToImport.shift();
						}
						
						if (_contacts.length) {
							// There are still contacts to import
							$.ajax({
								type: 'POST',
								url: 'import/',
								data: {
									username: username,
									token: token,
									contacts: '[' + _contacts.toString() + ']'
								},
								dataType: 'json',
								success: function(response) {
									if (response.success) {
										contactsAlreadyImported = contactsAlreadyImported.concat(_contacts);
										
										var value = $("#freshbooks-import-progressbar").progressbar('option', 'value');
										value += progressPerRequest;
										if (value > 100)
											value = 100;
										
										$("#freshbooks-import-progressbar").progressbar('option', 'value', value);
										$('#freshbooks-import-status').text('Imported ' + contactsAlreadyImported.length + ' Contacts. ' + contactsToImport.length + ' remaining...');
										
										importContacts();
									}
									else {
										enableForm();
										if (response.error)
											$('#freshbooks-import-status').text('Error: ' + response.error);
										else
											$('#freshbooks-import-status').text('Error while importing Contacts');
									}
								}
							});
						}
						else {
							// Time to finalize the import process
							$.ajax({
								type: 'POST',
								url: 'import/',
								data: {
									username: username,
									token: token,
									finalize: 'True'
								},
								dataType: 'json',
								success: function(response) {
									if (response.success) {
										// Finished Importing
										document.location.reload();
									}
									else {
										enableForm();
										$('#freshbooks-import-status').text('Error Finalizing the Import Process');
									}
								}
							});
						}
					}
					
					// This function is called recursively to get all the ids to import from Freshbooks
					var setupContactsImport = function() {
						$.ajax({
							type: 'POST',
							url: 'import-setup/' + setupPage + '/',
							data: {
								username: username,
								token: token
							},
							dataType: 'json',
							success: function(response) {
								if (response.success) {
									contactsToImport = contactsToImport.concat(response.contacts);
									
									if (response.keepProcessing) {
										setupPage++;
										setupContactsImport();
									}
									else {
										// Finished getting the ids, now start importing
										$('#freshbooks-import-progressbar').css('visibility', 'visible');
										$('#freshbooks-import-status').text('Importing Contacts');
										
										// Calculate the Progress Per Request
										progressPerRequest = Math.ceil( (CONTACTS_PER_REQUEST*100) / contactsToImport.length );
										
										// Import the Contacts
										importContacts();
									}
								}
								else {
									if (response.retry) {
										setupContactsImport();
									}
									else if(response.error) {
										enableForm();
										$('#freshbooks-import-status').text('Error: ' + response.error);
									}
								}
							}
						});
					};
					
					setupContactsImport();
				}, 
				"Cancel": function() {
					$('#username').val('');
					$('#token').val('');
					$("#freshbooks-import-progressbar").progressbar('option', 'value', 0);
					$("#freshbooks-import-progressbar").css('visibility', 'hidden');
					$('#freshbooks-import-status').text('');
					$(this).dialog("close");
				} 
			}
		});
		
		$('#freshbooks-import-link').click(function(){
			$('#freshbooks-import').dialog('open');
			return false;
		});
		
		$("#freshbooks-import-progressbar").progressbar();
		
	});
	/*** End Import Contacts Section ***/

	/*** Function called when the document is loaded, it initialize the events (import contacts and maps painting) ***/
	$(function () {
		$('#contacts').tabs({
			show:function(event,ui){
				if (ui.index === 1)
				{
					setupMap();
					$('#zoomcontacts').click(function(){
						map.setZoom(5);
					});
					$('#zoomCities').click(function(){
						map.setZoom(2);
					});
					$('#resetMap').click(function(){
						map.setCenter(new GLatLng(35, 5), 2);
					});
				}
				else 
					GUnload();
			}
		});
		
		// jqGrid set up
		var actionsFormatter = function(cellval, opts) {
			return '<a href="' + cellval.split('@')[0] + '" class="contact-listing-action">Details</a> | <a href="' + cellval.split('@')[1] + '" class="contact-listing-action">Edit</a> | <a href="' + cellval.split('@')[2] + '" class="contact-listing-action">Delete</a>';
		}
		
		if (hasContacts) {
			$('#contact-listing').jqGrid({
				datatype: "local",
				height: 450,
				colNames:['Name', 'Company', 'Address', 'City', 'State', 'Country', 'Zip Code', 'Actions'],
				colModel:[
					{name: 'name' ,index:'name', width: 150},
					{name: 'organization', index: 'organization', width: 100},
					{name: 'address', index: 'address', width: 240},
					{name: 'city', index: 'city', width: 70},
					{name: 'state', index: 'state', width: 70},
					{name: 'country', index: 'country', width: 70},
					{name: 'zip', index: 'zip', width: 80},
					{name: 'actions',index:'actions', width:120, sortable: false, formatter: actionsFormatter, align: 'center'}
				],
				autowidth: true,
				caption: 'Contact List'
			});
			
			for(var i=0; i <= contacts.length; i++)
				jQuery("#contact-listing").addRowData(i+1, contacts[i]);
		}
	});
