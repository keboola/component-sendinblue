# Sendinblue

## Overview

The component allows to send a transactional email via Sendinblue service. Prerequisities are:
1. Sendinblue account
2. Activated transactional email service
3. Defined templates

## Input and output

The sample of the configuration, including input and output tables, can be found in [component's repository](https://bitbucket.org/kds_consulting_team/kds-team.app-sendinblue/src/master/component_config/sample-config/). In general, an API key and at least one input table is needed to successfully run the component.

### Parameters

All of the parameters are required. The component will fail upon receiving invalid parameters. The sample of the configuration file can be found [here](https://bitbucket.org/kds_consulting_team/kds-team.app-sendinblue/src/master/component_config/sample-config/config.json).

#### API Key (`#apiKey`)

The API key for the Sendinblue service needs to be obtained from Sendinblue account settings. More information can be found in [the article](https://help.sendinblue.com/hc/en-us/articles/209467485-What-s-an-API-key-and-how-can-I-get-mine-).

### Input table

Multiple input tables can be specified on input. The input table has 2 mandatory columns and 3 optional columns. All columns must match the format used in [send transactional email](https://developers.sendinblue.com/reference#sendtransacemail) endpoint:

- `emailObject` - a valid array of object, identical with `to` object;
- `templateId` - id of a template, which will be sent to the recipient;
- `params` (opt.) - parameters to be passed along with the request, idential to `params`;
- `ccObject` (opt.) - an array of objects to which a copy of email will be sent, identical to `cc`;
- `bccObject` (opt.) - an array of objects to which a blind copy will be sent, identical to `bcc`.

If any of the mandatory columns is missing, a user error is raised. 

### Output table

As an output, 2 tables are returned:

- `messages` - contains information about message ID and recipients. The table is loaded incrementally,
- `errors` - contains information about errors

## Development

For development purposes use:
```
docker-compose build dev
docker-compose run --rm dev
```