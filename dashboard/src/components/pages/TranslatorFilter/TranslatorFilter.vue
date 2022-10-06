<template>
    <vue-fragment>

        <!-- Use inside of a v-row -->
        <v-col v-if="index !== null" sl>
            <v-select label="Filter by ARA"
                    v-model="ara_filter"
                    multiple
                    :items="Object.keys(index.ARA)"/>
        </v-col>
        <v-col v-if="index !== null" sl>
            <v-select label="Filter by KP"
                    v-model="kp_filter"
                    multiple
                    :items="index.KP"/>
        </v-col>

        <v-col sl>
            <v-select label="Filter subject categories"
                    multiple
                    :items="subject_categories"
                    v-model="subject_category_filter"/>
        </v-col>
        <v-col sl>
            <v-select label="Filter predicates"
                    multiple
                    :items="predicates"
                    v-model="predicate_filter"/>
        </v-col>
        <v-col sl>
            <v-select label="Filter object categories"
                    multiple
                    :items="object_categories"
                    v-model="object_category_filter"/>
        </v-col>

    </vue-fragment>
</template>
<script>
export default {
    name: "TranslatorFilter",
    props: {
        index: null,
    },
    data() {
        return {
            ara_filter: [],        
            kp_filter: [],
            subject_category_filter: [],
            predicate_filter: [],
            object_category_filter: [],
        }
    },
}
</script>
