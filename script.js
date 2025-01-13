const workstreamData = {
    'NBFF Storefronts': ['https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/nbff_storefronts_hours.csv', 'https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/nbff_storefronts_output.csv'],
    'ROSE Reviews': ['https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/rose_reviews_hours.csv', 'https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/rose_reviews_output.csv'],
    'US Admin': ['https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/us_admin_hours.csv', 'https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/us_admin_output.csv'],
    'Hitched/CA Lites Storefronts': ['https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/hitched_ca_lites_storefronts_hours.csv', 'https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/hitched_ca_lites_storefronts_output.csv'],
    'Hitched/CA Lites Admin': ['https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/hitched_ca_lites_admin_hours.csv', 'https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/hitched_ca_lites_admin_output.csv'],
    'Missing Attributes (US)': ['https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/missing_attributes_us_hours.csv', 'https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/missing_attributes_us_output.csv'],
    'Ad Units (Creation)': ['https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/ad_units_creation_hours.csv', 'https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/ad_units_creation_output.csv'],
    '360 Virtual Tours': ['https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/virtual_tours_hours.csv', 'https://raw.githubusercontent.com/ahorkan/Workstream-Output-Calculator/main/data/virtual_tours_output.csv']
};

document.getElementById('inputType').addEventListener('change', function() {
    const inputType = this.value;
    if (inputType === 'Hours') {
        document.getElementById('hoursLabel').style.display = 'inline';
        document.getElementById('hours').style.display = 'inline';
        document.getElementById('outputLabel').style.display = 'none';
        document.getElementById('output').style.display = 'none';
    } else if (inputType === 'Output') {
        document.getElementById('hoursLabel').style.display = 'none';
        document.getElementById('hours').style.display = 'none';
        document.getElementById('outputLabel').style.display = 'inline';
        document.getElementById('output').style.display = 'inline';
    } else {
        document.getElementById('hoursLabel').style.display = 'none';
        document.getElementById('hours').style.display = 'none';
        document.getElementById('outputLabel').style.display = 'none';
        document.getElementById('output').style.display = 'none';
    }
});

document.getElementById('calculateButton').addEventListener('click', function() {
    const workstream = document.getElementById('workstream').value;
    const inputType = document.getElementById('inputType').value;
    const hoursFile = workstreamData[workstream][0];
    const outputFile = workstreamData[workstream][1];

    Promise.all([
        fetch(hoursFile).then(response => response.text()).then(text => Papa.parse(text, { header: true }).data),
        fetch(outputFile).then(response => response.text()).then(text => Papa.parse(text, { header: true }).data)
    ]).then(([hoursData, outputData]) => {
        const hours = hoursData.map(row => parseFloat(row.hours)).filter(value => !isNaN(value));
        const output = outputData.map(row => parseFloat(row.output)).filter(value => !isNaN(value));

        const hoursMean = simpleStatistics.mean(hours);
        const outputMean = simpleStatistics.mean(output);

        const coefficients = simpleStatistics.linearRegressionLine(simpleStatistics.linearRegression(hours.map((h, i) => [h, output[i]])));

        let result;
        if (inputType === 'Hours') {
            const hoursInput = parseFloat(document.getElementById('hours').value);
            const predictedOutput = coefficients(hoursInput);
            result = `Predicted Output for ${hoursInput} hours in ${workstream}: ${predictedOutput}`;
        } else if (inputType === 'Output') {
            const outputInput = parseFloat(document.getElementById('output').value);
            const requiredHours = (outputInput - coefficients.b) / coefficients.m;
            result = `Required Hours for ${outputInput} output in ${workstream}: ${requiredHours}`;
        }

        document.getElementById('outputArea').innerHTML = result;
    });
});