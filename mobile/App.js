import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  Button,
  StyleSheet,
  ScrollView,
  Alert,
  Platform
} from 'react-native';
import * as Notifications from 'expo-notifications';
import { collection, addDoc } from 'firebase/firestore';
import { db } from './firebase.config';

// Configure how notifications appear when app is in foreground
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

export default function App() {
  const [pushToken, setPushToken] = useState(null);
  const [companies, setCompanies] = useState('');
  const [keywords, setKeywords] = useState('');
  const [isRegistered, setIsRegistered] = useState(false);

  useEffect(() => {
    registerForPushNotifications();
  }, []);

  const registerForPushNotifications = async () => {
    try {
      // Check if running on physical device
      if (Platform.OS === 'android' || Platform.OS === 'ios') {
        const { status: existingStatus } = await Notifications.getPermissionsAsync();
        let finalStatus = existingStatus;

        if (existingStatus !== 'granted') {
          const { status } = await Notifications.requestPermissionsAsync();
          finalStatus = status;
        }

        if (finalStatus !== 'granted') {
          Alert.alert('Error', 'Permission for notifications was denied');
          return;
        }

        // Get Expo Push Token
        const tokenData = await Notifications.getExpoPushTokenAsync({
          projectId: 'your-expo-project-id', // Replace with your Expo project ID
        });

        setPushToken(tokenData.data);
        console.log('Push Token:', tokenData.data);
      } else {
        // Just warning for simulator
        console.log('Must use physical device for push notifications');
      }
    } catch (error) {
      console.error('Error getting push token:', error);
      Alert.alert('Error', 'Failed to get push notification token');
    }
  };

  const handleSubscribe = async () => {
    if (!pushToken) {
      Alert.alert('Error', 'Push token not ready. Please try again (or use physical device).');
      return;
    }

    // Parse input
    const companyList = companies
      .split(',')
      .map(c => c.trim())
      .filter(Boolean);

    const keywordList = keywords
      .split(',')
      .map(k => k.trim())
      .filter(Boolean);

    if (companyList.length === 0) {
      Alert.alert('Error', 'Please enter at least one company');
      return;
    }

    try {
      // Save to Firestore
      await addDoc(collection(db, 'users'), {
        push_token: pushToken,
        filters: {
          companies: companyList,
          roles: [],
          keywords: keywordList,
        },
        active: true,
        created_at: new Date(),
      });

      Alert.alert('Success', 'You are now subscribed to job alerts!');
      setIsRegistered(true);
    } catch (error) {
      console.error('Error saving to Firestore:', error);
      Alert.alert('Error', 'Failed to subscribe. Please try again.');
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.header}>Career Alert Setup</Text>

      {pushToken && (
        <Text style={styles.tokenStatus}>Push notifications enabled ✓</Text>
      )}

      {!isRegistered ? (
        <>
          <Text style={styles.label}>
            Companies to monitor (comma separated):
          </Text>
          <TextInput
            style={styles.input}
            placeholder="Google, Microsoft, Anthropic, OpenAI"
            value={companies}
            onChangeText={setCompanies}
            multiline
          />

          <Text style={styles.label}>
            Job keywords (comma separated):
          </Text>
          <TextInput
            style={styles.input}
            placeholder="new grad, entry level, 2026"
            value={keywords}
            onChangeText={setKeywords}
            multiline
          />

          <Button
            title="Subscribe for Alerts"
            onPress={handleSubscribe}
            disabled={!pushToken}
          />
        </>
      ) : (
        <View style={styles.successContainer}>
          <Text style={styles.successText}>
            You're all set! You'll receive notifications when new jobs matching
            your preferences are posted.
          </Text>
          <Text style={styles.monitoringText}>
            Monitoring: {companies}
          </Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 40,
    paddingTop: 80,
    backgroundColor: '#fff',
  },
  header: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  tokenStatus: {
    color: 'green',
    marginBottom: 20,
    textAlign: 'center',
  },
  label: {
    fontSize: 16,
    marginBottom: 8,
    marginTop: 16,
    fontWeight: '600',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 12,
    borderRadius: 8,
    fontSize: 16,
    minHeight: 60,
  },
  successContainer: {
    marginTop: 40,
    padding: 20,
    backgroundColor: '#f0f9ff',
    borderRadius: 8,
  },
  successText: {
    fontSize: 16,
    marginBottom: 12,
    lineHeight: 24,
  },
  monitoringText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '600',
  },
});