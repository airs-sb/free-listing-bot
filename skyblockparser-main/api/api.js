const { getNetworth } = require('skyhelper-networth');
const express = require('express');

const app = express();
const port = process.env.PORT || 3000;

app.use(express.json({ limit: '20mb' }));


app.post('/networth', async (req, res) => {
    const { profile, bank, museumData } = req.body;
    try {
        const networth = await getNetworth(profileData=profile, bankBalance=bank, { v2Endpoint: true, museumData});
        res.send(networth);
    }
    catch (err) {
        res.status(400).send(err.message);
    }

});

app.listen(port, () => {
    console.log(`Running on port ${port}`);
});