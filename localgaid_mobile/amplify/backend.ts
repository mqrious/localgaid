import { defineBackend } from '@aws-amplify/backend';
import { Effect, Policy, PolicyStatement } from "aws-cdk-lib/aws-iam";
import { Bucket } from "aws-cdk-lib/aws-s3";
import { auth } from './auth/resource';
// import { data } from './data/resource';

/**
 * @see https://docs.amplify.aws/react/build-a-backend/ to add storage, functions, and more
 */
const backend = defineBackend({
  auth,
  // data,
});


const customBucketStack = backend.createStack("localgaid-dev-bucket-stack");


// Import existing bucket
const customBucket = Bucket.fromBucketAttributes(customBucketStack, "localgaid-dev-bucket", {
  bucketArn: "arn:aws:s3:::localgaid-dev",
  region: "ap-southeast-2"
});


backend.addOutput({
  storage: {
    aws_region: customBucket.env.region,
    bucket_name: customBucket.bucketName,
    // optional: `buckets` can be used when setting up more than one existing bucket
    buckets: [
      {
        aws_region: customBucket.env.region,
        bucket_name: customBucket.bucketName,
        name: customBucket.bucketName,
        /*
          optional: `paths` can be used to set up access to specific 
          bucket prefixes and configure user access types to them
        */ 
        paths: {
          "audio-guides/*": {
            // "write" and "delete" can also be added depending on your use case
            guest: ["get", "list"], 
          },
        },
      }
    ]
  },
});


/*
  Define an inline policy to attach to Amplify's unauth role
  This policy defines how unauthenticated/guest users can access your existing bucket
*/ 
const unauthPolicy = new Policy(backend.stack, "customBucketUnauthPolicy", {
  statements: [
    new PolicyStatement({
      effect: Effect.ALLOW,
      actions: ["s3:GetObject"],
      resources: [`${customBucket.bucketArn}/audio-guides/*`],
    }),
    new PolicyStatement({
      effect: Effect.ALLOW,
      actions: ["s3:ListBucket"],
      resources: [
        `${customBucket.bucketArn}`,
        `${customBucket.bucketArn}/*`
      ],
      conditions: {
        StringLike: {
          "s3:prefix": ["audio-guides/", "audio-guides/*"],
        },
      },
    }),
  ],
});


// Add the policies to the unauthenticated user role
backend.auth.resources.unauthenticatedUserIamRole.attachInlinePolicy(
  unauthPolicy,
);
