const fwd_inputList = [
    'fwd_commodity',
    'fwd_quantity',
    'fwd_line',
    'fwd_rate',
    'fwd_container_type',
    'fwd_oceanfreight_total',
    'fwd_thc',
    'fwd_bl',
    'fwd_muc',
    'fwd_seal',
    'fwd_facility',
    'fwd_toll',
    'fwd_isps_total'
];

const lead_inputList = [
    'Shipper_id',
    'Employee_id',
    'shipper_name',
    'shipper_contact',
    'shipper_email',
    'forward_check',
    'cha_check',
    'trans_check',
    'fwd_date',
    'In_queue'
    ];

const cha_inputList = [
    'cha_origin',
    'cha_cha',
    'cha_shipper',
    'cha_forwarder',
    'cha_commodity',
    'cha_weight',
    'cha_container_type',
    'cha_charge',
    'cha_portstuffing',
    'cha_agency',
    'cha_phyto',
    'cha_fumial',
    'cha_fumime',
    'cha_coo',
    'cha_craftpaper',
    'cha_silica'
];

const transport_inputList = [
    'transport_origin',
    'transport_destination',
    'transport_charge'
];

function loadInputMap(inputList){
    let inputMap = {}
    inputList.map((elementId, index) =>{
        try{
            let value = document.getElementById(elementId).value;
        inputMap[elementId] = value;
        }catch(err){
            console.log(err);
        }

    });
    return inputMap;
}


function postData(data){
    console.log('sending data');
	console.log(data);
	axios({
		method: 'post',
		url: 'http://localhost:8080/sales/lead/',
		data: {
			data,
		},
	})
	.then(result => {
	    console.log(result);
	})
	.catch(err => console.log(err));
}


function getLeadData(){
    const lead_inputMap = loadInputMap(lead_inputList);
    const cha_inputMap = loadInputMap(cha_inputList);
    const fwd_inputMap = loadInputMap(fwd_inputList);
    const transport_inputMap = loadInputMap(transport_inputList);
    const data = {
        lead_inputMap,
        cha_inputMap,
        fwd_inputMap,
        transport_inputMap,
    }
    postData(data);
    console.log(lead_inputMap);
    console.log(cha_inputMap);
    console.log(fwd_inputMap);
    console.log(transport_inputMap);
}


function axiosCall(){
    console.log('axios calling')
    axios.get('http://jsonplaceholder.typicode.com/todos')
    .then(function (response) {
      console.log('response');
      console.log(response);
    })
    .catch(function (error) {
      resultElement.innerHTML = generateErrorHTMLOutput(error);
    });
}

