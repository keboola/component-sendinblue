# Sendinblue

## Overview

The component allows to send a transactional email via Sendinblue service. Prerequisities are:
1. Sendinblue account
2. Activated transactional email service
3. Defined templates

## Input and output

The sample of the configuration, including input and output tables, can be found in [component's repository](https://bitbucket.org/kds_consulting_team/kds-team.app-sendinblue/src/master/component_config/sample-config/). In general, 3 parameters and at least one input table is needed to successfully run the component.

### Parameters

All of the parameters are required. The component will fail upon receiving invalid parameters. The sample of the configuration file can be found [here](https://bitbucket.org/kds_consulting_team/kds-team.app-sendinblue/src/master/component_config/sample-config/config.json).

#### API Key (`#apiKey`)

The API key for the Sendinblue service needs to be obtained from Sendinblue account settings. More information can be found in [the article](https://help.sendinblue.com/hc/en-us/articles/209467485-What-s-an-API-key-and-how-can-I-get-mine-).

#### Processing in batches (`batch.usage`)

A boolean value marking, whether batch processing should be used. If `false`, emails are sent one-by-one to each recipient in a separate message. If market as `true`, the list of recipients is split according to parameters `batch.size` and emails are sent in batches.

#### Batch size (`batch.size`)

Integer value marking the size of batch for emails. The parameter is ignored if `batch.usage=false`.

### Input table

Multiple input tables can be specified on input. The input table has 3 mandatory columns:

- `email` - an email address of the recipient
- `name` - name of the recipient
- `templateId` - id of a template, which will be sent to the recipient.

If any of the columns is missing, a user error is raised. 

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