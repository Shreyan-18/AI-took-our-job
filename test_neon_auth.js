/**
 * Neon Managed Better Auth Verification Script
 * Demonstrates email/password signup and reading back the verified user session.
 * Adheres to Neon Auth best practices from the neon-auth skill.
 */

const { createAuthClient } = require('@neon/auth');
require('dotenv').config();

async function runAuthVerification() {
  const authUrl = process.env.NEON_AUTH_BASE_URL;
  if (!authUrl) {
    throw new Error('NEON_AUTH_BASE_URL is not defined in environment.');
  }

  console.log('✓ Initializing Neon Auth client with branch endpoint...');
  const authClient = createAuthClient(authUrl);

  const timestamp = Date.now();
  const testEmail = `citizen.${timestamp}@redtape.gov.in`;
  const testName = 'Verified Citizen Demo';
  // Standard test password meeting length requirements
  const testPassword = 'Password123!Secure';

  console.log(`✓ Signing up new test citizen: ${testEmail}`);
  const signUpRes = await authClient.signUp.email(
    {
      email: testEmail,
      password: testPassword,
      name: testName,
      callbackURL: 'http://localhost:8765',
    },
    {
      headers: {
        Origin: 'http://localhost:8765',
      },
    }
  );

  if (signUpRes.error) {
    console.error('✗ Sign up failed:', signUpRes.error);
    process.exit(1);
  }

  const userId = signUpRes.data?.user?.id;
  console.log('✓ Sign up successful:');
  console.log(`  - User ID: ${userId}`);
  console.log(`  - Name: ${signUpRes.data?.user?.name}`);
  console.log(`  - Email: ${signUpRes.data?.user?.email}`);
  console.log(`  - Email Verified: ${signUpRes.data?.user?.emailVerified}`);

  console.log('✓ Signing in with email & password to verify session...');
  const signInRes = await authClient.signIn.email(
    {
      email: testEmail,
      password: testPassword,
      callbackURL: 'http://localhost:8765',
    },
    {
      headers: {
        Origin: 'http://localhost:8765',
      },
    }
  );

  if (signInRes.error) {
    console.error('✗ Sign in failed:', signInRes.error);
    process.exit(1);
  }

  console.log('✓ Sign in successful:');
  console.log(`  - Verified Current User: ${signInRes.data?.user?.name} (${signInRes.data?.user?.email})`);
  console.log(`  - User ID: ${signInRes.data?.user?.id}`);
  console.log(`  - Active Session Token Present: ${Boolean(signInRes.data?.token)}`);
  console.log('\n★ All Neon Better Auth operations passed successfully!');
}

runAuthVerification().catch((err) => {
  console.error('Execution error:', err);
  process.exit(1);
});
