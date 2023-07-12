const { Kafka } = require('kafkajs')
const TradingView = require('/usr/src/app/@mathieuc/tradingview');


const args = process.argv.slice(2);

const market = args[0];
const stock = args[1];
const timeframe = args[2];
const strategy = args[3];
const days = args[4];
const to_time = args[5]; /* this one to set time until e.g "00:00:00 GMT" */
const to_datetime = String(args[6]); /* this one to set datetime until e.g "Fri, 31 Mar 2023" */
const topic_name = args[7]

let client = new TradingView.Client();


var date = new Date();
date.setDate(date.getDate() - 1);
let utcStr = date.toUTCString();
console.log('Extracting '+days+' days from now...');

var data = {};
data.table = [];


async function produceMessages(topic, message) {
  const kafka = new Kafka({
    brokers: ['kafka-service:9092'],
  });

  const producer = kafka.producer();

  await producer.connect();

  await producer.send({
    topic: topic,
    messages: [{ value: message }],
  });

  await producer.disconnect();
}


const run = async () => {
  console.log('Setting Kafka ...')
  let chart = new client.Session.Chart();


  chart.setMarket( market + ':' + stock,  {
    timeframe: timeframe,
    to: Math.round(Date.now() / 1000) - 86400*days,
    range: -1,
  });

  let publicFmp = TradingView.searchIndicator(strategy)

  publicFmp.then(async (indicator) => {

    TradingView.getIndicator(indicator[0].id).then(async (indic) => {

      if (args.length > 5) {
        for (var x = 5; x < args.length; x++) {
          Object.keys(indic.inputs).forEach(key => {
            if (indic.inputs[key].inline === args[x].split('=')[0]) {
              var arg_value = args[x].split('=')[1];
              if (['float', 'integer'].includes(indic.inputs[key].type)) {
                arg_value = parseInt(arg_value)
              }
              indic.inputs[key].value = arg_value;
            }
          })
        }
      }

      const study = new chart.Study(indic);

      study.onUpdate(() => {
        var materials = study.periods[0];
        var t = new Date(study.periods[0].$time * 1000);
        var t1 = t.toUTCString();

        var str1 = `{
          "title": "`+ stock +`",
          "strategy": "`+ strategy +`",
          "time": "`+ t1 + `",
          "timeframe": "`+ timeframe + `",
          "`+ topic_name +`": "`+ chart.periods[0].close +`"
        }`;

        console.log(str1)

        var info = JSON.parse(str1);
        var result = {};

        Object.keys(info)
        .forEach(key => result[key] = info[key]);
        Object.keys(materials)
        .forEach(key => result[key] = materials[key]);

        data.table.push(result);


        if (t1.substring(t1.length - 12) === to_time) {
          if (t1.substring(0,16) === to_datetime) {
            console.log('Operation accomplished. Exiting.');

            produceMessages(topic_name, JSON.stringify(data)).catch((error) => {
                console.error('Error producing messages:', error);
            });

            client.end();
          }
        }
        setTimeout(() => {
          chart.fetchMore(-2);
        }, 1);

      });
  });
  });
}
client.end();
run().catch(console.error)

