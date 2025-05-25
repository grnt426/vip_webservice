import React, { useState } from 'react';
import { TextField, Button, Typography, Container, Box, Paper, Alert, CircularProgress, Stepper, Step, StepLabel } from '@mui/material';

// Define expected response types from backend (can be moved to a types file)
interface ValidateResponse {
    username: string;
    message: string;
}

const API_KEY_LENGTH = 72;
const MIN_PASSWORD_LENGTH = 8; // Example minimum password length

const RegistrationPage: React.FC = () => {
    const [apiKey, setApiKey] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [username, setUsername] = useState<string>('');
    
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [validationSuccess, setValidationSuccess] = useState<string | null>(null);
    const [registrationSuccess, setRegistrationSuccess] = useState<string | null>(null);

    const [activeStep, setActiveStep] = useState(0);

    const steps = ['Enter API Key', 'Set Password & Register'];

    const handleApiKeyChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setApiKey(event.target.value.trim());
        setError(null); // Clear error when user types
        setValidationSuccess(null);
        if (activeStep === 1) setActiveStep(0); // Reset to first step if user changes API key
    };

    const handlePasswordChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setPassword(event.target.value);
        setError(null); // Clear error when user types
    };

    const validateApiKeyFormat = (): boolean => {
        if (apiKey.length !== API_KEY_LENGTH) {
            setError(`API Key must be ${API_KEY_LENGTH} characters long.`);
            return false;
        }
        // Add more client-side format checks if needed (e.g., regex for characters)
        return true;
    };

    const handleValidateApiKey = async () => {
        if (!validateApiKeyFormat()) return;

        setIsLoading(true);
        setError(null);
        setValidationSuccess(null);

        try {
            const response = await fetch('/api/users/validate-api-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'API key validation failed.');
            }
            
            const validatedData = data as ValidateResponse;
            setUsername(validatedData.username);
            setValidationSuccess(validatedData.message || `API Key validated for user: ${validatedData.username}`);
            setActiveStep(1); // Move to next step

        } catch (err: any) {
            setError(err.message || 'An unexpected error occurred during API key validation.');
            setUsername('');
            setActiveStep(0);
        } finally {
            setIsLoading(false);
        }
    };

    const handleRegister = async () => {
        if (password.length < MIN_PASSWORD_LENGTH) {
            setError(`Password must be at least ${MIN_PASSWORD_LENGTH} characters long.`);
            return;
        }
        if (!username) {
            setError('API Key must be validated first.'); // Should not happen if UI flow is correct
            return;
        }

        setIsLoading(true);
        setError(null);
        setRegistrationSuccess(null);

        try {
            const response = await fetch('/api/users/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey, password: password, username: username }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Registration failed.');
            }

            // const registrationData = data as RegistrationResponse;
            setRegistrationSuccess(`User ${data.username} registered successfully! You can now log in.`);
            // Optionally redirect to login page or clear form
            // props.history.push('/login'); 
            setApiKey(''); // Clear fields on success
            setPassword('');
            setUsername('');
            setActiveStep(0); // Reset to first step

        } catch (err: any) {
            setError(err.message || 'An unexpected error occurred during registration.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Container maxWidth="md">
            <Paper elevation={3} sx={{ padding: 4, marginTop: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom align="center">
                    User Registration
                </Typography>
                
                <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4}}>
                    {steps.map((label) => (
                        <Step key={label}>
                            <StepLabel>{label}</StepLabel>
                        </Step>
                    ))}
                </Stepper>

                {error && <Alert severity="error" sx={{ marginBottom: 2 }}>{error}</Alert>}
                {validationSuccess && activeStep === 1 && <Alert severity="success" sx={{ marginBottom: 2 }}>{validationSuccess}</Alert>}
                {registrationSuccess && <Alert severity="success" sx={{ marginBottom: 2 }}>{registrationSuccess}</Alert>}

                <Box component="form" noValidate autoComplete="off">
                    {activeStep === 0 && (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                            <Typography variant="h6">Step 1: Validate API Key</Typography>
                            <Typography variant="body1" gutterBottom>
                                Please generate a Guild Wars 2 API key with the following permissions: 
                                <strong>account, guilds, characters</strong>. 
                                You can create an API key at 
                                <a href="https://account.arena.net/applications" target="_blank" rel="noopener noreferrer"> account.arena.net/applications</a>.
                            </Typography>
                            <TextField
                                label="GW2 API Key"
                                variant="outlined"
                                fullWidth
                                value={apiKey}
                                onChange={handleApiKeyChange}
                                error={apiKey.length > 0 && apiKey.length !== API_KEY_LENGTH}
                                helperText={apiKey.length > 0 && apiKey.length !== API_KEY_LENGTH ? `API Key must be ${API_KEY_LENGTH} characters` : ''}
                                disabled={isLoading}
                                sx={{ marginBottom: 2 }}
                            />
                            <Button
                                variant="contained"
                                color="primary"
                                onClick={handleValidateApiKey}
                                disabled={isLoading || apiKey.length !== API_KEY_LENGTH}
                                fullWidth
                                sx={{ padding: 1.5}}
                            >
                                {isLoading ? <CircularProgress size={24} /> : 'Validate API Key'}
                            </Button>
                        </Box>
                    )}

                    {activeStep === 1 && username && (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, marginTop: 3 }}>
                             <Typography variant="h6">Step 2: Set Password for {username}</Typography>
                            <TextField
                                label="Password"
                                type="password"
                                variant="outlined"
                                fullWidth
                                value={password}
                                onChange={handlePasswordChange}
                                error={password.length > 0 && password.length < MIN_PASSWORD_LENGTH}
                                helperText={password.length > 0 && password.length < MIN_PASSWORD_LENGTH ? `Password must be at least ${MIN_PASSWORD_LENGTH} characters` : ''}
                                disabled={isLoading}
                                sx={{ marginBottom: 2 }}
                            />
                            <Button
                                variant="contained"
                                color="primary"
                                onClick={handleRegister}
                                disabled={isLoading || password.length < MIN_PASSWORD_LENGTH || !username}
                                fullWidth
                                sx={{ padding: 1.5}}
                            >
                                {isLoading ? <CircularProgress size={24} /> : 'Register Account'}
                            </Button>
                             <Button
                                variant="outlined"
                                onClick={() => { 
                                    setActiveStep(0); 
                                    setError(null); 
                                    setValidationSuccess(null); 
                                    // Do not clear API key so user can try again or fix it
                                }}
                                disabled={isLoading}
                                fullWidth
                                sx={{ mt: 1}}
                            >
                                Back to API Key Entry
                            </Button>
                        </Box>
                    )}
                </Box>
            </Paper>
        </Container>
    );
};

export default RegistrationPage; 