import 'package:flutter_test/flutter_test.dart';

import 'package:localgaid_mobile/repositories/place_repository.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

Future<void> main() async {
  setUp(() async {
    try {
      Supabase.instance;
    } catch (ex) {
      await Supabase.initialize(
        url: 'https://sevbhseieyyrfgaccvjm.supabase.co',
        anonKey:
            'public-api-key',
      );
    }
  });

  test('Fetch places', () async {
    final supabaseClient = Supabase.instance.client;
    final placeRepository = PlaceRepositoryImpl(supabaseClient: supabaseClient);

    final places = await placeRepository.fetchPlaces();

    print(places.length);
  });

  test('Get place by id', () async {
    final supabaseClient = Supabase.instance.client;
    final placeRepository = PlaceRepositoryImpl(supabaseClient: supabaseClient);

    final (place, audioGuides) = await placeRepository.getPlace(id: 5);

    print(place);

    print(audioGuides.length);
  });
}
